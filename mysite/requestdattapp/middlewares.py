import time

from django.http import HttpRequest, HttpResponse


# ==========================================================
# FUNCTION MIDDLEWARE
# Добавляет User-Agent в объект request
# ==========================================================

def set_useragent_on_request_middleware(get_response):
    """
    Вызывается ОДИН РАЗ при запуске Django.
    Здесь создается middleware.
    """
    print("Middleware initialized")

    def middleware(request: HttpRequest):
        """
        Вызывается ПРИ КАЖДОМ HTTP-запросе.
        """

        print("Before get response")

        # Получаем User-Agent браузера
        request.user_agent = request.META.get(
            "HTTP_USER_AGENT",
            "",
        )

        # Передаем запрос следующему middleware
        # или View
        response = get_response(request)

        print("After get response")

        # Возвращаем ответ обратно пользователю
        return response

    return middleware


# ==========================================================
# CLASS MIDDLEWARE
# Считает количество запросов, ответов и исключений
# ==========================================================

class CountRequestsMiddleware:
    """
    Middleware в виде класса.

    Показывает:
        • сколько пришло запросов;
        • сколько отправлено ответов;
        • сколько произошло исключений.
    """

    def __init__(self, get_response):
        """
        Выполняется один раз
        при запуске приложения.
        """

        self.get_response = get_response

        self.request_count = 0
        self.response_count = 0
        self.exception_count = 0

    def __call__(self, request: HttpRequest):
        """
        Выполняется при каждом запросе.
        """

        # Считаем запросы
        self.request_count += 1

        print(f"Request count: {self.request_count}")

        # Передаем запрос дальше
        response = self.get_response(request)

        # После получения ответа
        self.response_count += 1

        print(f"Response count: {self.response_count}")

        return response

    def process_exception(
        self,
        request: HttpRequest,
        exception: Exception,
    ):
        """
        Вызывается,
        если во View произошло исключение.
        """

        self.exception_count += 1

        print(
            f"Exception count: {self.exception_count}"
        )


# ==========================================================
# THROTTLING MIDDLEWARE
# Ограничивает слишком частые запросы
# ==========================================================

class ThrottlingMiddleware:
    """
    Простая защита от слишком частых запросов.

    Если пользователь отправляет запросы
    чаще одного раза в две секунды,
    возвращается ошибка 429.
    """

    def __init__(self, get_response):
        """
        Выполняется один раз
        при запуске сервера.
        """

        self.get_response = get_response

        # Здесь будем хранить
        # IP пользователя
        # и время последнего запроса
        self.users = {}

        # Интервал между запросами
        self.delay = 2

    def __call__(self, request: HttpRequest):

        # Получаем IP пользователя
        ip = request.META.get("REMOTE_ADDR")

        # Текущее время
        current = time.time()

        print(f"IP: {ip}")

        # Последнее обращение пользователя
        last = self.users.get(ip)

        # Если пользователь уже заходил
        if last is not None:

            # Проверяем интервал
            if current - last < self.delay:

                print("Too many requests!")

                return HttpResponse(
                    "Too many requests",
                    status=429,
                )

        # Запоминаем время запроса
        self.users[ip] = current

        print("Request allowed")

        # Передаем запрос дальше
        response = self.get_response(request)

        return response