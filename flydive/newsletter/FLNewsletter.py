from newsletter.FLHtmlGenerator import FLHtmlGenerator
from common import tools

class FLNewsletter():

    def __init__(self):
        self.generator = FLHtmlGenerator()

    def sendEmail(self, emailList, attachmentList):
        message = "Szczegóły znalezionych lotów znajdziesz w załącznikach."
        title = "Raport lotów z aplikacji Flydive"
        attachments = "-a "
        attachments += " -a ".join(attachmentList)
        emails = " ".join(emailList)
        command = """echo "{}" | mutt {} -s"{}" -- {}""".format(message, attachments, title, emails)
        tools.run_cmd(command)

    def prepare_HTML(self, calculatedFlights):
        for i, trip in enumerate(calculatedFlights):
            html = self.generator.generate_html(trip)
            
            if "name" in trip['CONF']:
                trip_name = trip['CONF']['name']
            else:
                trip_name = "fly_report"

            with open("logs/{}.html".format(trip_name), "w") as file:
                file.write(html)
                emailList = trip['CONF']['email']
                self.sendEmail(emailList, [ file.name ])
                file.close()
