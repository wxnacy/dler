package dler

import (
	"bytes"
	"compress/gzip"
	"fmt"
	"io"
	"time"

	"github.com/imroc/req/v3"
)

var globalRequest = NewRequest()

func GetGlobalRequst() *Request {
	return globalRequest
}

func NewRequest() *Request {
	Client := req.C().SetTimeout(30 * time.Second)

	// 不设置User-Agent，让库使用默认的
	Client.SetCommonHeaders(map[string]string{
		"Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
		"Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
		"Accept-Encoding": "gzip, deflate, br",
		"Cache-Control":   "no-cache",
		"Pragma":          "no-cache",
	})

	// 启用自动重定向，最多允许10次重定向
	Client.SetRedirectPolicy(req.MaxRedirectPolicy(10))

	return &Request{Client: Client}
}

type Request struct {
	Client    *req.Client
	isVerbose bool
}

func (r *Request) SetHeader(key, value string) *Request {
	r.Client.SetCommonHeader(key, value)
	return r
}

func (r *Request) SetHeaders(hds map[string]string) *Request {
	r.Client.SetCommonHeaders(hds)
	return r
}

func (r *Request) EnableVerbose() *Request {
	r.isVerbose = true
	r.Client.DevMode().EnableDumpAllWithoutBody()
	return r
}

func (r *Request) GetReader(url string) (io.Reader, error) {
	b, err := r.GetBytes(url)
	if err != nil {
		return nil, err
	}

	// 添加调试信息
	if r.isVerbose {
		fmt.Printf("URL: %s\nContent (first 200 chars): %s\n", url, string(b)[:min(200, len(b))])
	}

	return bytes.NewReader(b), nil
}

func (r *Request) GetBytes(url string) ([]byte, error) {
	resp, err := r.Client.R().Get(url)
	err = r.checkResponse(resp, err)
	if err != nil {
		return nil, err
	}

	// 获取原始字节数据
	rawBytes := resp.Bytes()

	// 检查内容编码
	contentEncoding := resp.Header.Get("Content-Encoding")
	if contentEncoding == "gzip" {
		// 手动解压 gzip 内容
		gzipReader, err := gzip.NewReader(bytes.NewReader(rawBytes))
		if err != nil {
			return nil, fmt.Errorf("failed to create gzip reader: %v", err)
		}
		defer gzipReader.Close()

		// 读取解压后的内容
		decompressedBytes, err := io.ReadAll(gzipReader)
		if err != nil {
			return nil, fmt.Errorf("failed to decompress gzip content: %v", err)
		}

		if r.isVerbose {
			fmt.Printf("Decompressed content length: %d\n", len(decompressedBytes))
		}

		return decompressedBytes, nil
	}

	return rawBytes, nil
}

func (r *Request) GetBytesByRange(url string, start, end int) ([]byte, error) {
	resp, err := r.Client.R().
		SetHeader("Range", fmt.Sprintf("bytes=%d-%d", start, end)).Get(url)
	err = r.checkResponse(resp, err)
	if err != nil {
		return nil, err
	}

	// 检查服务器是否支持 Range 请求
	contentRange := resp.Header.Get("Content-Range")
	if contentRange == "" {
		// 服务器不支持 Range 请求，回退到普通 GET 请求
		return r.GetBytes(url)
	}

	return resp.Bytes(), nil
}

func (r *Request) Head(url string) (*req.Response, error) {
	resp, err := r.Client.R().Head(url)
	err = r.checkResponse(resp, err)
	if err != nil {
		return resp, err
	}
	if r.isVerbose {
		fmt.Printf("%s Header: %s", url, resp.HeaderToString())
	}
	return resp, nil
}

func (r *Request) checkResponse(resp *req.Response, err error) error {
	url := resp.Request.URL.String()
	if r.isVerbose {
		fmt.Printf("检查响应: URL=%s, Error=%v, StatusCode=%d, IsError=%v\n", url, err, resp.StatusCode, resp.IsError())
	}
	if err != nil {
		return fmt.Errorf("%s: %v", url, err)
	}
	if resp.IsError() {
		return fmt.Errorf("%s: %v", url, resp.Status)
	}
	if resp.Err != nil {
		return fmt.Errorf("%s: %v", url, resp.Err)
	}
	return nil
}

// 添加辅助函数
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
