from app.connectors.web_crawler import is_ssrf_safe_url


def test_ssrf_protection_blocks_localhost_and_private_ips():
    assert is_ssrf_safe_url("http://localhost:8000/internal") is False
    assert is_ssrf_safe_url("http://127.0.0.1:5432") is False
    assert is_ssrf_safe_url("http://10.0.0.1/admin") is False
    assert is_ssrf_safe_url("http://192.168.1.1/router") is False
    assert is_ssrf_safe_url("http://169.254.169.254/latest/meta-data") is False
    assert is_ssrf_safe_url("http://server.internal/metrics") is False


def test_ssrf_protection_allows_valid_public_urls():
    assert is_ssrf_safe_url("https://example.org/about") is True
    assert is_ssrf_safe_url("https://google.com/search") is True
