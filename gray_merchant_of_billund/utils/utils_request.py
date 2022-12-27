from functools import wraps

from requests import ConnectionError, Session
from retrying import retry  # type: ignore
from stem import Signal
from stem.control import Controller

from gray_merchant_of_billund.constants.gmob import (
    BRICKLINK_LOGIN_ENDPOINT,
    TOR_CONTROLLER_PORT,
)
from gray_merchant_of_billund.model.exception import BricklinkLoginException
from gray_merchant_of_billund.secrets import (
    BRICKLINK_PASSWORD,
    BRICKLINK_USERNAME,
    TOR_PASSWORD,
)


def _retry_on_connection_error(exc):
    return isinstance(exc, ConnectionError)


def _http_request_retry(http_request):
    # retries a HTTP request in case of ConnectionError with an exponential
    # backoff policy and additional random waits between 1 and 2 seconds.
    # It gives up after 5 attempts or after 60 seconds have passed.
    @retry(
        retry_on_exception=_retry_on_connection_error,
        stop_max_attempt_number=5,
        stop_max_delay=60 * 1000,
        wait_random_min=1 * 1000,
        wait_random_max=2 * 1000,
        wait_exponential_multiplier=1000,
    )
    def _execute_with_retry(request, *args, **kwargs):
        return http_request(request, *args, **kwargs)

    return wraps(http_request)(_execute_with_retry)


@_http_request_retry
def execute_http_request(request_fn, url, timeout=(3 * 20, 120), headers={}):
    # Assumes the request_fn is from requests module.
    # Timeout is a tuple (connection_timeout, read_timeout).
    # Further details here:
    # https://3.python-requests.org/user/quickstart/#timeouts
    # Caller should catch ConnectionError and HTTPError, or more broadly
    # requests.exceptions.RequestException
    response = request_fn(url, timeout=timeout, headers=headers)
    response.raise_for_status()
    return response


def get_unathenticated_session():
    return Session()


def get_bricklink_authenticated_session():
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/108.0.0.0 "
        "Safari/537.36",
    }

    data = {
        "userid": BRICKLINK_USERNAME,
        "password": BRICKLINK_PASSWORD,
        "override": "false",
        "keepme_loggedin": "true",
        "impersonate": "false",
        "pageid": "MAIN",
        "login_to": "",
    }
    session = Session()
    response = session.post(
        BRICKLINK_LOGIN_ENDPOINT,
        headers=headers,
        data=data,
    )
    if response.status_code == 200 and response.ok:
        return session
    raise BricklinkLoginException()


def get_tor_session():
    session = Session()
    session.proxies = {
        "http": "socks5h://localhost:9050",
        "https": "socks5h://localhost:9050",
    }
    return session


def renew_tor_ip():
    with Controller.from_port(port=TOR_CONTROLLER_PORT) as controller:
        controller.authenticate(password=TOR_PASSWORD)
        controller.signal(Signal.NEWNYM)
