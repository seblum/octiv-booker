from datetime import date 


def get_button_day(days_to_be_bookable : int) -> str:
    week_days = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
    today = date.today().weekday()
    future_day = today + days_to_be_bookable
    future_day = week_days[future_day]

    def _get_xpath_butten(d: int) -> str:
        return f"/html/body/div/div[5]/div/div[3]/div[{d}]/div/p"

    match future_day:
        case "Thursday":
            pass
        case "Friday":
            button_day = _get_xpath_butten(6)
        case "Saturday":
            pass
        case "Sunday":
            pass
    return button_day, future_day


def _get_slot(day: str, book: bool = True) -> str:
    # set paths for weightligting slot, etc
    
    def _get_xpath_book(d: int) -> str:
        return f"/html/body/div/div[5]/div/div[9]/div/div[1]/div[3]/button"

    def _get_xpath_cancel(d: int) -> str:
        return f"/html/body/div/div[5]/div/div[9]/div/div[2]/div[3]/button"

    class_thu = 3 # weightlifting
    class_sat = 4 # gynmastics
    class_sun = 3 # weightlifting

    match day:
        case "Thursday":
            return _get_xpath_book(class_thu) if book else _get_xpath_cancel(class_thu)
        case "Saturday":
            return "Not found"
        case "Sunday":
            return "I'm a teapot"
        case _:
            return "Something's wrong with the internet"
