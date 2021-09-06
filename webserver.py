#from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith('/hello'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "Hello!"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"></form>'''
                output += "</body></html>"
                self.wfile.write(bytes(output, "utf-8"))
                print(output)
                return

            if self.path.endswith('/hola'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "&#161Hola!<a href='/hello'>Back to Hello page</a>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hola'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>'''
                output += "</body></html>"
                self.wfile.write(bytes(output, "utf-8"))
                print(output)
                return


            if self.path.endswith('/restaurants'):
                restaurants_list = session.query(Restaurant).all()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                print("Lista de restaurantes:")
                print(restaurants_list)
                
                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>Insert a new restaurant</a>"
                output += "<h1>Lista de restaurantes</h1>"
                
                for restaurant in restaurants_list:
                    output += restaurant.name + "</br>"
                    output += "<a href='/restaurants/" + str(restaurant.id) + "/edit'>Edit</a></br>"
                    output += "<a href='/restaurants/" + str(restaurant.id) + "/delete'>Delete</a></br></br>"
                
                output += "</body></html>"

                self.wfile.write(bytes(output, "utf-8"))
                print(output)
                return
            
            if self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                output = ""
                output += "<html><body>"
                output += "<h1>Insert a new restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><input name='message' type='text' placeholder='New Restaurant Name'><input type='submit' value='Insert'></form>"
                output += "</body></html>"

                self.wfile.write(bytes(output, "utf-8"))
                print(output)
                return
            
            if self.path.endswith('/edit'):
                restaurant_id = self.path.split("/")[2]
                
                restaurant_to_update = session.query(Restaurant).filter_by(id = restaurant_id).one()
                if restaurant_to_update != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    output = "<html><body>"
                    output += "<h1>" + str(restaurant_to_update.name) + "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/" + str(restaurant_to_update.id) + "/edit'><input name='newname' type='text' placeholder='" + str(restaurant_to_update.name) + "'><input type='submit' value='Rename'></form>"
                    output += "</body></html>"
                
                    self.wfile.write(bytes(output, "utf-8"))
              
            if self.path.endswith('/delete'):
                restaurant_id = self.path.split("/")[2]

                restaurant_to_delete = session.query(Restaurant).filter_by(id = restaurant_id).one()
                if restaurant_to_delete != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    output = "<html><body>"
                    output += "<h1>Are you sure you want to delete " + str(restaurant_to_delete.name) + "?</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/" + str(restaurant_to_delete.id) + "/delete'><input type='submit' value='Delete'></form>"
                    output += "</body></html>"
                
                    self.wfile.write(bytes(output, "utf-8"))

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                # HEADERS are now in dict/json style container
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                # boundary data needs to be encoded in a binary format
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                content_len = int(self.headers.get('Content-length'))
                pdict['CONTENT-LENGTH'] = content_len
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
            
                # Creamos el nuevo restaurante con el nombre que nos da el usuario
                new_restaurant = Restaurant(name = messagecontent[0])
                session.add(new_restaurant)
                session.commit()
            
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                
                return

            if self.path.endswith("/edit"):
                # HEADERS are now in dict/json style container
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                # boundary data needs to be encoded in a binary format
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                content_len = int(self.headers.get('Content-length'))
                pdict['CONTENT-LENGTH'] = content_len
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newname')
                
                restaurant_id = self.path.split("/")[2]
                
                # UPDATE
                restaurant_to_update = session.query(Restaurant).filter_by(id = restaurant_id).one()
                if restaurant_to_update != []:
                    restaurant_to_update.name = messagecontent[0]
                    session.add(restaurant_to_update)
                    session.commit()
                    
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                
                return

            if self.path.endswith("/delete"):                
                restaurant_id = self.path.split("/")[2]
                
                # DELETE
                restaurant_to_delete = session.query(Restaurant).filter_by(id = restaurant_id).one()
                if restaurant_to_delete != []:
                    session.delete(restaurant_to_delete)
                    session.commit()
                    
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            
        except:
            raise

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print("Web server running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()