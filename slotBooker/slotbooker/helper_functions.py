from datetime import date 

def get_day(days_before_bookable : int) -> (str, bool):
    week_days = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
    today = date.today().weekday()
    future_day = today + days_before_bookable
    # future_day_int if future_day_int < 7 else future_day_int - 7
    if future_day < 7:
        return week_days[future_day], False
    else:
        future_day = future_day - 7
        return week_days[future_day], True


def get_day_button(day_to_book : str) -> str:

    def _get_xpath_button(day_index: int) -> str:
        return f"/html/body/div/div[5]/div/div[3]/div[{day_index}]/div/p"

    # monday:2 ; sunday:8
    match day_to_book:
        case "Monday":
            day_button = _get_xpath_button(2)
        case "Tuesday":
            day_button = _get_xpath_button(3)
        case "Wednesday":
            day_button = _get_xpath_button(4)
        case "Thursday":
            day_button = _get_xpath_button(5)
        case "Friday":
            day_button = _get_xpath_button(6)
        case "Saturday":
            day_button = _get_xpath_button(7)
        case "Sunday":
            day_button = _get_xpath_button(8)
    return day_button


def _get_booking_slot(day_to_book: str, book_action: bool = True) -> str:
    # set paths for weightligting slot, etc
    
    def _get_xpath_book(slot: int) -> str:
        return f"/html/body/div/div[5]/div/div[{slot}]/div/div[1]/div[3]/button"

    def _get_xpath_cancel(slot: int) -> str:
        return f"/html/body/div/div[5]/div/div[{slot}]/div/div[2]/div[3]/button"

    # box above
    # /html/body/div/div[5]/div/div[6]/div/div[1]
    # weightlifting box
    # /html/body/div/div[5]/div/div[7]/div/div[1]

    # for i in all:
    #     f"/html/body/div/div[5]/div/div[{i}]/div/div[1]/div[2]/p[1]"
    #     /html/body/div/div[5]/div/div[7]/div/div[1]/div[2]/p[1]

    # WebElement e = driver.findElement(By.xpath("//*[text()='Weightlifting']"));

    # System.out.println("Element with text(): " + e.getText() );
    
    # "//*[text() = 'Weightlifting']"
    # //example[contains(text(), 'Hello')]

    # button_str= "/div[3]/button"
    # f'/html/body/div/div[5]/div/div[{ where_sth_is_weightliftig  }]/div/div[1]' + button_str
    
    class_thu = 3 # weightlifting
    # /html/body/div/div[5]/div/div[16]/div/div[1]/div[3]/button
    class_sat = 4 # gynmastics
    # /html/body/div/div[5]/div/div[7]/div/div[1]/div[3]/button
    class_sun = 3 # weightlifting
    # /html/body/div/div[5]/div/div[7]/div/div[1]/div[3]/button

    match day_to_book:
        case "Monday":
            return "TBD"
        case "Tuesday":
            return "TBD"
        case "Wednesday":
            return "TBD"
        case "Thursday":
            return _get_xpath_book(class_thu) if book_action else _get_xpath_cancel(class_thu)
        case "Friday":
            return "TBD"
        case "Saturday":
            return "TBD"
        case "Sunday":
            return "TBD"
