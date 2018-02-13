import requests, json, sys, datetime
from pprint import pprint as pp

# CONV is used to convert arguments to a proper format as needed by api
CONV ={"--date":"dateFrom","--from":"flyFrom","--to":"to"}
ARGS = sys.argv[1:]
INFO = {
  "passengers": [
    {
      "firstName": "Erik",
      "lastName": "Travels",
      "title": "Mr",
      "birthday": "1990-10-10",
      "documentID": "D25845822",
      "category": "adults",
      "email":"erik.citterberg@gmail.com"
     },
                ],
  "currency": "EUR",
        }

# main function
def SearchAndBook(args):
    try:
        flight = findFlight(payload(args)[0])
        displayInfo(flight)
        bags = payload(args)[1]
        book(flight["booking_token"],bags)
    except IndexError:
        print("It seems you used wrong airport code.")

# creates a dictionary for parameters of requests.get function
def payload(args):
    form = {"typeFlight":"oneway","sort":"price","adults":1,"v":2}
    pload = []
    bags = 0
    rettime = 0


    for i in range(0,len(args)):
        if args[i] in CONV.keys():
            form[CONV[args[i]]] = args[i+1]
        elif args[i] == "--fastest":
            form["sort"] = "duration"
        elif args[i] == "--return":
            form["typeFlight"] = "round"
        elif args[i] == "--bags":
            bags = args[i+1]
        if args[i] == "--return":
            rettime = int(args[i+1])

    form["dateFrom"] = datetime.datetime.strptime(form["dateFrom"], '%Y-%m-%d').strftime('%d/%m/%Y')
    form["dateTo"] = form["dateFrom"]

    if form["typeFlight"] == "round":
        form["returnTo"] = datetime.datetime.strptime(form["dateFrom"], '%d/%m/%Y') + datetime.timedelta(days=rettime)
        form["returnTo"] = datetime.datetime.strptime(str(form["returnTo"]), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
        form["returnFrom"] = form["returnTo"]

    return form,bags

# requests flight from api, return first flight from ordered list depending on param. from user
def findFlight(payload):
    r = requests.get("https://api.skypicker.com/flights?", params=payload)
    return json.loads(r.text)["data"][0]

# simple output of basic information about requested flight
def displayInfo(flight):
    print("{}: {}\n{}: {}".format("From",flight["cityFrom"], "To", flight["cityTo"]))
    print(datetime.datetime.fromtimestamp(flight["dTime"]))
    print("{}: {}\n{}: {}\n{}: {}".format("Price",flight["conversion"],"Baggage price",
    flight["bags_price"], "Duration", flight["fly_duration"]))
    if "return_duration" in flight.keys():
        print("{}: {}".format("Return duration",flight["return_duration"]))
    print("{}: {}".format("Route",flight["routes"]))

# posts dictionary of passangers with neccesary key:value pairs (token, bags) to booking api
def book(token,bnum):
    headers = {"Content-Type": "application/json"}
    INFO["bags"] = bnum
    INFO["booking_token"] = token
    r = requests.post("http://128.199.48.38:8080/booking?", headers=headers, data = json.dumps(INFO))
    print(r.text)

# to distinguish from where it is run and to take care of cases with not enough or wrong arguments
if __name__ == "__main__":
    try:
        SearchAndBook(ARGS)
    except KeyError:
        print("Your arguments are no good here, sorry.")
