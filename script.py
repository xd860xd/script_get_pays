import argparse



class Application(object):

    def __init__(self, ) -> None:
        self.data = None
        
        self.DAYS = [
            "MO",
            "TU",
            "WE",
            "TH",
            "FR",
            "SA",
            "SU",
        ]

        self.HRS= [
            "00:01-09:00",
            "09:01-18:00",
            "18:01-00:00"
        ]

        self.PAYS = [
            {
                "days": self.DAYS[:5],
                "hr" : self.HRS[0],
                "amount": "25 USD"

            },
            {
                "days": self.DAYS[:5],
                "hr" : self.HRS[1],
                "amount": "15 USD"
            },
            {
                "days": self.DAYS[:5],
                "hr" : self.HRS[2],
                "amount": "20 USD"   
            },
            {
                "days": self.DAYS[5:],
                "hr" : self.HRS[0],
                "amount": "30 USD"

            },
            {
                "days": self.DAYS[5:],
                "hr" : self.HRS[1],
                "amount": "20 USD"
            },
            {
                "days": self.DAYS[5:],
                "hr" : self.HRS[2],
                "amount": "25 USD"   
            }
        ]

    def convert_txt(self):
        data = None
        with open('file.txt') as f:
            text = f.read()
            data = text.split("\n")

        with open('file_result.txt', "w") as f:
            for line in data:            
                result = self.return_amount(line)
                f.write(result+ "\n")

    def menu(self):

        inp = input("Introduce un registro: ")
        try:
            self.return_amount(inp)
        except Exception as ex:
            print(ex)
            print("\nAsegurese que se esta insartando con este formato:\n\
                RENE=MO10:00-12:00,TU10:00-12:30,TH01:00-03:00,SA14:00-18:00,SU20:00-21:00\n")
        
        inp = input("Desea agregar otro registro [y/N]: ")
        if inp.capitalize() == "N":
            return 0
        else:
            self.menu()

    def return_amount(self, line):
        try:
            name = line.split("=")[0]
            
            data = line.split("=")[1]
        except Exception:
            raise Exception("Formato invalido")

        days = self.validate_input(data)

        amount = self.get_amount(days)

        print(f"The amount to pay {name} is: {amount} USD")
        return f"The amount to pay {name} is: {amount} USD"

    def validate_input(self,inp):


        days = [{"day": day[:2], "time": day[2:]} for day in inp.split(",")]

        for day in days:
            if day["day"] not in self.DAYS:
                raise Exception(f"El dia {day['day']} no es una abreviación valida")

            [hr_init, hr_end] = day["time"].split("-")

            hr_init = self.validate_hr(hr_init)
            hr_end = self.validate_hr(hr_end)

            day["initial_hr"] = hr_init
            day["end_hr"] = hr_end

            if hr_init[0]>hr_end[0]:
                raise Exception("Error horarios no compatibles")
            elif hr_init[0]==hr_end[0] and hr_init[1]>hr_end[1]:
                raise Exception("Error horarios no compatibles")

        return days

        
    def validate_hr(self,hrs):
        try:
            [hr, min] = hrs.strip().split(":")
        except Exception:
            raise Exception("Formato invalido")
        hr = int(hr)
        if hr not in list(range(0,24)):
            raise Exception(f"{hr} no es una hora valida")

        min = int(min)
        if min not in list(range(0,60)):
            raise Exception(f"{min} no es un minuto valido")
        return [hr, min]


    def get_amount(self,days):
        
        total_amount = 0

        for day in days:

            init = day["initial_hr"]
            end = day["end_hr"]

            if (init[0]>18 or (init[0]==18 and init[1]>=1)) or (init[0] == 0 and init[1]==0):
                init_in =  "18:01-00:00"
            elif (init[0]>9 or (init[0]==9 and init[1]>=1)) or (init[0] == 18 and init[1]==0):
                init_in = "09:01-18:00"
            else:
                init_in = "00:01-09:00"

            if (end[0]>18 or (end[0]==18 and end[1]>=1)) or (end[0] == 0 and end[1]==0):
                end_in = "18:01-00:00"
            elif (end[0]>9 or (end[0]==9 and end[1]>=1)) or (end[0] == 18 and end[1]==0):
                end_in =  "09:01-18:00"
            else:
                end_in = "00:01-09:00"

            if init_in == end_in:
                
                amoutn_per_hr = self.get_amout_per_hr(end_in, day["day"])
                hrs=end[0]-init[0]                
                mins = end[1]-init[1]
                amount_aux = (mins + hrs*60)*amoutn_per_hr/60


            elif init_in == "00:01-09:00" and end_in=="18:01-00:00":
                amoutn_per_hr = self.get_amout_per_hr(init_in, day["day"])
                first_mount = self.get_mount_time_init_to_end_turn(init[0], init[1], init_in,amoutn_per_hr )

                amoutn_per_hr = self.get_amout_per_hr("09:01-18:00", day["day"])
                second_mount = self.get_mount_time_init_to_end_turn(9, 1, "09:01-18:00",amoutn_per_hr )
            
                amoutn_per_hr = self.get_amout_per_hr(end_in, day["day"])

                third_mout = self.get_mount_init_turn_to_end(end[0], end[1], end_in, amoutn_per_hr )

                amount_aux = first_mount + second_mount + third_mout

            else:
                amoutn_per_hr = self.get_amout_per_hr(init_in, day["day"])
                first_mount = self.get_mount_time_init_to_end_turn(init[0], init[1], init_in,amoutn_per_hr )

                amoutn_per_hr = self.get_amout_per_hr(end_in, day["day"])
                third_mout = self.get_mount_init_turn_to_end(init[0], init[1], end_in,amoutn_per_hr )
                amount_aux = first_mount + third_mout

            
            total_amount+=amount_aux   

        return total_amount  

    def get_amout_per_hr(self, schedule, day):

        pays = filter(lambda pay: pay["hr"]==schedule and day in pay["days"], self.PAYS)

        return int(list(pays)[0]["amount"].split(" ")[0])

            
    def get_mount_time_init_to_end_turn(self, hr, minut, schedule, mount_per_hr):
        hr_limit = int(schedule.split("-")[1].split(":")[0])

        if hr in [ 9, 18, 0 ] and minut == 0:
            return 0

        hrs = hr_limit - hr
        mins = minut + hrs*60
        return mins * mount_per_hr/60

    def get_mount_init_turn_to_end(self, hr, minut, schedule, mount_per_hr):
        hr_init = int(schedule.split("-")[0].split(":")[0])

        hrs = hr-hr_init
        mins = minut-1 + hrs*60
        return mins * mount_per_hr/60


if __name__ == "__main__":
    app = Application()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("arg", type = str, help="'interactive' or 'test_file'")
    args = parser.parse_args()
    if args.arg == "test_file":
        app.convert_txt()
    elif args.arg == "interactive":
        app.menu()
    else:
        print("Argumento invalido")



    