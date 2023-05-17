from dataclasses import dataclass


@dataclass
class ProxyInfo:
    proxy_id: str # Идентификатор прокси
    proxy_exp: str # Дата и время, до которых прокси оплачено
    proxy_login: str # Логин для авторизации
    proxy_pass: str # Пароль для авторизации
    proxy_hostname: str # Адрес прокси-сервера
    proxy_host_ip: str # IP-адрес прокси сервера
    proxy_independent_http_hostname: str # Независящий от смены оборудования адрес HTTP прокси-сервера
    proxy_independent_http_host_ip: str # Независящий от смены оборудования IP-адрес HTTP прокси-сервера
    proxy_independent_socks5_hostname: str # Независящий от смены оборудования адрес SOCKS5 прокси-сервера
    proxy_independent_socks5_host_ip: str # Независящий от смены оборудования IP-адрес SOCKS5 прокси-сервера
    proxy_independent_port: str # Независящий от смены оборудования порт
    proxy_http_port: str # HTTP порт прокси
    proxy_socks5_port: str # Socks5 порт прокси
    proxy_operator: str # Мобильный оператор
    proxy_geo: str # ГЕО прокси
    proxy_auto_renewal: str # Автопродление. 1 - включено, 0 - выключено
    proxy_change_ip_url: str # Ссылка для смены ip-адреса
    proxy_reboot_time: int # Таймер смены IP-адреса
    proxy_ipauth: str # IP-адрес для авторизации без логина и пароля
    proxy_groups_name: str | None # Если прокси состоит в группе, то в этом поле будет название группы
    proxy_auto_change_equipment: str # Настройка автоматической смены оборудования, 0 - отключена, 1 - не ограничивать, 2 - страна, 3 - область, край, регион, 4 - город
    proxy_key: str 
    eid: str # Идентификатор оборудования

    @property
    def proxies_dict(self) -> dict[str, str]:
        proxy_str = f"http://{self.proxy_login}:{self.proxy_pass}@{self.proxy_independent_http_hostname}:{self.proxy_independent_port}"
        return {
            'http': proxy_str,
            'https': proxy_str
        }