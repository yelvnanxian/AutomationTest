"""作用：在请求发送前安全注入Bearer Token、Cookie和CSRF认证信息。"""

import threading
import time


class AuthenticationExpiredError(RuntimeError):
    """认证已过期且无法刷新时抛出。"""


class BearerTokenProvider:
    """管理Bearer Token，并在过期前通过回调刷新一次。"""

    def __init__(
        self,
        access_token,
        refresh_token=None,
        expires_in=None,
        expires_at=None,
        refresh_callback=None,
        refresh_margin_seconds=30,
        header_name='Authorization',
        token_prefix='Bearer',
    ):
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires_at = self._resolve_expires_at(expires_in, expires_at)
        self._refresh_callback = refresh_callback
        self._refresh_margin_seconds = refresh_margin_seconds
        self._header_name = header_name
        self._token_prefix = token_prefix
        self._refresh_lock = threading.Lock()

    @staticmethod
    def _resolve_expires_at(expires_in, expires_at):
        if expires_at is not None:
            return float(expires_at)
        if expires_in is not None:
            return time.time() + float(expires_in)
        return None

    def _is_expired(self):
        return (
            self._expires_at is not None
            and time.time() >= self._expires_at - self._refresh_margin_seconds
        )

    def _refresh_if_needed(self):
        if not self._is_expired():
            return
        if self._refresh_callback is None:
            raise AuthenticationExpiredError('Bearer Token已过期且未配置刷新回调')

        with self._refresh_lock:
            if not self._is_expired():
                return
            token_data = self._refresh_callback(self._refresh_token)
            if isinstance(token_data, str):
                token_data = {'access_token': token_data}
            if not isinstance(token_data, dict) or not token_data.get('access_token'):
                raise AuthenticationExpiredError('Token刷新回调未返回access_token')
            self.set_token(
                token_data['access_token'],
                refresh_token=token_data.get('refresh_token', self._refresh_token),
                expires_in=token_data.get('expires_in'),
                expires_at=token_data.get('expires_at'),
            )

    def set_token(
        self,
        access_token,
        refresh_token=None,
        expires_in=None,
        expires_at=None,
    ):
        """更新Token数据，不记录或输出Token内容。"""
        if not access_token:
            raise ValueError('access_token不能为空')
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires_at = self._resolve_expires_at(expires_in, expires_at)

    def apply(self, headers, cookies):
        """在请求前确保Token有效并注入认证Header。"""
        self._refresh_if_needed()
        if not self._access_token:
            raise AuthenticationExpiredError('Bearer Token为空')
        headers[self._header_name] = '%s %s' % (
            self._token_prefix,
            self._access_token,
        )

    def clear(self):
        self._access_token = None
        self._refresh_token = None
        self._expires_at = None


class CookieAuthProvider:
    """向单次请求注入固定认证Cookie，不修改Session动态Cookie。"""

    def __init__(self, cookies=None):
        self._cookies = dict(cookies or {})

    def set_cookies(self, cookies):
        self._cookies = dict(cookies or {})

    def apply(self, headers, cookies):
        cookies.update(self._cookies)

    def clear(self):
        self._cookies.clear()


class CsrfTokenProvider:
    """向Header注入CSRF Token，可选同步注入对应Cookie。"""

    def __init__(
        self,
        token,
        header_name='X-CSRF-Token',
        cookie_name=None,
    ):
        self._token = token
        self._header_name = header_name
        self._cookie_name = cookie_name

    def set_token(self, token):
        if not token:
            raise ValueError('CSRF Token不能为空')
        self._token = token

    def apply(self, headers, cookies):
        if not self._token:
            raise AuthenticationExpiredError('CSRF Token为空')
        headers[self._header_name] = self._token
        if self._cookie_name:
            cookies[self._cookie_name] = self._token

    def clear(self):
        self._token = None


class CompositeAuthProvider:
    """按顺序组合多个认证Provider，例如Session Cookie加CSRF Token。"""

    def __init__(self, *providers):
        self._providers = list(providers)

    def apply(self, headers, cookies):
        for provider in self._providers:
            provider.apply(headers, cookies)

    def clear(self):
        for provider in self._providers:
            provider.clear()
