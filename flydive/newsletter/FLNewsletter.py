from newsletter.FLHtmlGenerator import FLHtmlGenerator

class FLNewsletter():

    def __init__(self):
        self.generator = FLHtmlGenerator()

    def prepare_HTML(self, calculatedFlights):
        for i, trip in enumerate(calculatedFlights):
            html = self.generator.generate_html(trip)
            with open("logs/{}.html".format(i), "w") as file:
                file.write(html)
                file.close()
