package main

import (
	"bytes"
	"crypto/sha256"
	"crypto/tls"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

// ProbeRequest represents a single HTTP request to probe.
type ProbeRequest struct {
	ID        string            `json:"id"`
	Method    string            `json:"method"`
	URL       string            `json:"url"`
	Headers   map[string]string `json:"headers"`
	Body      string            `json:"body"`
	MaskKeys  []string          `json:"mask_keys"`
	TimeoutMs int               `json:"timeout_ms"`
}

// ProbeResult represents the wire-level evidence result.
type ProbeResult struct {
	ID               string              `json:"id"`
	StatusCode       int                 `json:"status_code"`
	LatencyMs        int64               `json:"latency_ms"`
	Headers          map[string][]string `json:"headers"`
	RawBodySHA256    string              `json:"raw_body_sha256"`
	MaskedBodySHA256 string              `json:"masked_body_sha256"`
	BodyPreview      string              `json:"body_preview"`
	Error            string              `json:"error,omitempty"`
}

func maskJSON(data []byte, maskKeys []string) []byte {
	if len(maskKeys) == 0 {
		return data
	}
	var obj interface{}
	if err := json.Unmarshal(data, &obj); err != nil {
		return data // Return unmasked if not valid JSON
	}

	keysSet := make(map[string]bool)
	for _, k := range maskKeys {
		keysSet[strings.ToLower(k)] = true
	}

	var stripKeys func(v interface{}) interface{}
	stripKeys = func(v interface{}) interface{} {
		switch val := v.(type) {
		case map[string]interface{}:
			clean := make(map[string]interface{})
			for k, child := range val {
				if !keysSet[strings.ToLower(k)] {
					clean[k] = stripKeys(child)
				}
			}
			return clean
		case []interface{}:
			clean := make([]interface{}, len(val))
			for i, item := range val {
				clean[i] = stripKeys(item)
			}
			return clean
		default:
			return val
		}
	}

	cleanedObj := stripKeys(obj)
	cleanedJSON, err := json.Marshal(cleanedObj)
	if err != nil {
		return data
	}
	return cleanedJSON
}

func executeProbe(client *http.Client, req ProbeRequest) ProbeResult {
	result := ProbeResult{
		ID:      req.ID,
		Headers: make(map[string][]string),
	}

	var bodyReader io.Reader
	if req.Body != "" {
		bodyReader = bytes.NewBufferString(req.Body)
	}

	httpReq, err := http.NewRequest(req.Method, req.URL, bodyReader)
	if err != nil {
		result.Error = fmt.Sprintf("failed to build request: %v", err)
		return result
	}

	for k, v := range req.Headers {
		httpReq.Header.Set(k, v)
	}

	start := time.Now()
	resp, err := client.Do(httpReq)
	result.LatencyMs = time.Since(start).Milliseconds()

	if err != nil {
		result.Error = fmt.Sprintf("http error: %v", err)
		return result
	}
	defer resp.Body.Close()

	result.StatusCode = resp.StatusCode
	for k, v := range resp.Header {
		result.Headers[k] = v
	}

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		result.Error = fmt.Sprintf("failed to read body: %v", err)
		return result
	}

	// Compute raw body hash
	rawHash := sha256.Sum256(bodyBytes)
	result.RawBodySHA256 = hex.EncodeToString(rawHash[:])

	// Compute masked body hash
	maskedBytes := maskJSON(bodyBytes, req.MaskKeys)
	maskedHash := sha256.Sum256(maskedBytes)
	result.MaskedBodySHA256 = hex.EncodeToString(maskedHash[:])

	// Preview (first 512 bytes)
	if len(bodyBytes) > 512 {
		result.BodyPreview = string(bodyBytes[:512]) + "...[truncated]"
	} else {
		result.BodyPreview = string(bodyBytes)
	}

	return result
}

func main() {
	batchMode := flag.Bool("batch", false, "Read JSON array of ProbeRequest from stdin")
	concurrency := flag.Int("concurrency", 10, "Maximum concurrent probes in batch mode")
	timeoutSec := flag.Int("timeout", 15, "Default HTTP timeout in seconds")
	insecureTLS := flag.Bool("insecure", true, "Skip TLS verification for pentest targets")
	flag.Parse()

	transport := &http.Transport{
		TLSClientConfig:     &tls.Config{InsecureSkipVerify: *insecureTLS},
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 20,
		IdleConnTimeout:     90 * time.Second,
	}

	client := &http.Client{
		Transport: transport,
		Timeout:   time.Duration(*timeoutSec) * time.Second,
	}

	if *batchMode {
		var requests []ProbeRequest
		decoder := json.NewDecoder(os.Stdin)
		if err := decoder.Decode(&requests); err != nil {
			fmt.Fprintf(os.Stderr, "Error decoding stdin JSON: %v\n", err)
			os.Exit(1)
		}

		results := make([]ProbeResult, len(requests))
		var wg sync.WaitGroup
		sem := make(chan struct{}, *concurrency)

		for i, req := range requests {
			wg.Add(1)
			sem <- struct{}{}
			go func(idx int, r ProbeRequest) {
				defer wg.Done()
				defer func() { <-sem }()
				results[idx] = executeProbe(client, r)
			}(i, req)
		}

		wg.Wait()
		output, _ := json.MarshalIndent(results, "", "  ")
		fmt.Println(string(output))
		return
	}

	// Fallback single test probe
	fmt.Println("fastprobe v1.0.0 - High-Speed Evidence Replay Prober (Go engine)")
	fmt.Println("Use -batch to pipe JSON requests via stdin.")
}
