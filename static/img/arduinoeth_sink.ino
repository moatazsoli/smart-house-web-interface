/***************************************************************************/
/*                                                                         */
/*  This sketch sets 8 digital and all 6 analogic outputs of the Arduino   */
/*  board according to the inputs read by actuator instance on Paraimpu.   */
/*  v1 - December 2011                                                     */
/*                                                                         */
/*  http://paraimpu.crs4.it                                                */
/*                                                                         */
/*  This sketch is released under GPL v3. For more details, please read    */
/*  http://www.gnu.org/licenses/gpl-3.0.txt                                */
/***************************************************************************/


#include <SPI.h>
#include <Ethernet.h>

// MAC Address of your Arduino Ethernet shield
byte mac[6] = { 0x90, 0xA2, 0xDA, 0x00, 0x22, 0x22 };



IPAddress server( 156, 148, 18, 164 );
EthernetClient client;
int p;
int i;
String data = String();
char c;
boolean take;
int waiting;
int n;
int v;
int digits;
int jump;

void setup() {
  for(i = 2; i < 10; i++){
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  for(i = 14; i < 20; i++){
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  //Serial.begin(9600);
  	waiting = 0;
	while (Ethernet.begin(mac) == 0  && waiting < 800){
		delay(10);
		waiting++;
	}
	//  Serial.println(Ethernet.localIP());

  delay(1000);
}

void loop() {
  if (client.connect(server, 80)) {
    client.println("GET /use?token=e8dd0be7-6dd5-4a51-9c2d-5dc9f56e8f5b HTTP/1.1");
    client.println("Host: paraimpu.crs4.it");
    client.println();
    data = String();
    take = false;
    //Serial.println("           ");
    //Serial.println("reading ...");
    waiting = 0;
    while (!client.available() && waiting < 500){
        delay(10);
        waiting++;
    }
    while (client.available()){
        c = client.read();
        if (c == '}'){
            run();
            break;
        }
        else if(c == '{'){
          take = true;
        }
        else if(c == '\\' || c == ' '){}
        else {
          if (take){
              data.concat(String(c));
          }
        }
     }
  }
  client.stop();
  delay(1000);
}

void run(){
  if(data.charAt(2) == 'X' ){ //all data
    writeAll(data.charAt(7));
    data = "";
  }
  else {
    p = 0;
    n = 0;
    v = 0;
    digits = 0;
    jump = 0;
    while (p < data.length()){
      if (data.charAt(p + 1) == 'A'){
        n = int(data.charAt(p + 2)) - 48;
        n = n + 14;
        jump = 9;
        if (data.charAt(p + 6) == 'L'){
          digitalWrite(n, LOW);
        }
        else {
          digitalWrite(n, HIGH);
        }
      }
      else {
        n = (int(data.charAt(p + 2)) - 48) * 10;
        n = n + int(data.charAt(p + 3)) - 48;
        if (data.charAt(p + 7) == 'L'){
          digitalWrite(n, LOW);
          jump = 10;
        }
        else if (data.charAt(p + 7) == 'H'){
          digitalWrite(n, HIGH);
          jump = 10;
        }
        else {
          v = 0;
          if (isDigit(data.charAt(p + 8))){
            v = int(data.charAt(p + 8)) - 48 + (int(data.charAt(p + 7)) - 48) * 10 + (int(data.charAt(p + 6)) - 48) * 100;
            jump = 10;
          }
          else if (isDigit(data.charAt(p + 7))){
            v = int(data.charAt(p + 7)) - 48 + (int(data.charAt(p + 6)) - 48) * 10;
            jump = 9;
          }
          else {
            v = int(data.charAt(p + 6)) - 48;
            jump = 8;
          }
          analogWrite(n, v);
        }
      }
      p = p + jump;
    }
    data = "";
  }
}

void writeAll(char out) {
  if(out == 'L'){
    for(i = 2; i < 10; i++){
      digitalWrite(i, LOW);
    }
    for(i = 14; i < 20; i++){
      digitalWrite(i, LOW);
    }
  }
  else{
    for(i = 2; i < 10; i++){
      digitalWrite(i, HIGH);
    }
    for(i = 14; i < 20; i++){
      digitalWrite(i, HIGH);
    }
  }
}

boolean isDigit(char ch){
  if(ch >= 48 && ch <= 75){
    return true;
  }
  return false;
}