package dler

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/imroc/req/v3"
)

var globalRequest = NewRequest()

func GetGlobalRequst() *Request {
	return globalRequest
}

func NewRequest() *Request {
	Client := req.C().SetTimeout(5 * time.Second)
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
	return bytes.NewReader(b), nil
}

func (r *Request) GetBytes(url string) ([]byte, error) {
	resp, err := r.Client.R().Get(url)
	err = r.checkResponse(resp, err)
	if err != nil {
		return resp.Bytes(), err
	}
	return resp.Bytes(), nil
}

func (r *Request) GetBytesByRange(url string, start, end int) ([]byte, error) {
	resp, err := r.Client.R().
		SetHeader("Range", fmt.Sprintf("bytes=%d-%d", start, end)).Get(url)
	err = r.checkResponse(resp, err)
	if err != nil {
		return resp.Bytes(), err
	}
	return resp.Bytes(), nil
}

func (r *Request) Head(url string) (http.Header, error) {
	resp, err := r.Client.R().Head(url)
	err = r.checkResponse(resp, err)
	if err != nil {
		return resp.Header, err
	}
	if r.isVerbose {
		fmt.Printf("%s Header: %s", url, resp.HeaderToString())
	}
	return resp.Header, nil
}

func (r *Request) checkResponse(resp *req.Response, err error) error {
	url := resp.Request.URL.String()
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
