#include <SoftwareSerial.h>
#include <TinyGPS++.h>


// LORA Define Function
#define RX_Pin 7 // for Globalstar LM-210H 915Mhz TX
#define TX_Pin 8 // for Globalstar LM-210H 915Mhz RX
#define P1 3  
#define P2 5  
String SendString = "";    // string to hold input
String ReceiveString = "";    // string to hold input
long int TxCh[8]= {916100000, 916300000, 916400000, 915100000, 915300000, 915500000, 915700000, 915900000};
SoftwareSerial LoRa(RX_Pin, TX_Pin);  // 傳送腳,接收腳 
#define LoRaBaud 57600

// Define GPS Function 
SoftwareSerial Serial_connection(10,11); //Rx-pin, Tx Pin 11
static const uint32_t GPSBaud=9600; 
TinyGPSPlus gps; 
float val =28.5458;
float lon =28.5458;
float lati =28.5458;
float sp =0; 
float al = 0; 

byte gpsData="";
// Accelerometer Pin Function 
const int accelerx = A0;
const int accelery = A1;
const int accelerz = A2;
const int accelerx1= A3;
const int accelery1= A4;
const int accelerz1= A5;
float accelex; 
float acceley;
float accelez; 
float accele1x; 
float accele1y;
float accele1z; 
String x= "";
String y= ""; 
String z= ""; 
String x1= ""; 
String y1= ""; 
String z1= ""; 



void setup() {

  // Open serial communications and wait for port to open:
  Serial.begin(9600);
      while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  LoRa_init();
  LoRa_WAN();
  //LoRa_parameter();
  delay(2000);

  Serial_connection.begin(GPSBaud);
   
}

void loop() { 
// GPS Encode 
   while ( Serial_connection.available()>0) {
    ; // wait for serial port to connect. Needed for native USB port only
       
   
   
     gps.encode(Serial_connection.read());
      if( gps.location.isUpdated() ){   
 
      
  
      //Serial.println("Satellite Count: "); 
      //Serial.println(gps.satellites.value()); 
      val = (gps.satellites.value());
      //Serial.println("Latitude: ");
      //Serial.println(gps.location.lat(), 6); 
      lati = (gps.location.lat()); 
      //Serial.println("longtitude: "); 
     // Serial.println(gps.location.lng()); 
      lon = gps.location.lng();
      //Serial.println("speed MPH: "); 
      //Serial.println(gps.speed.mph()); 
      sp = (gps.speed.mps()); 
     // Serial.println("alltitude Feet: "); 
      //Serial.println(gps.altitude.feet());
      al =  gps.altitude.feet(); 
      //Serial.println("");  
      String v = String(val);
      String lo= String (lon, 6); 
      String la= String  (lati, 6); 
      String s = String (sp);
      String a = String (al); 
      
    
   delay(100); 
   
// Accelerometer 
     accelex = analogRead(accelerx);
     acceley = analogRead(accelery);
     accelez = analogRead(accelerz);
     accele1x = analogRead(accelerx1);
     accele1y = analogRead(accelery1);
     accele1z = analogRead(accelerz1);
        String x = String ( accelex);
        String y = String ( acceley);
        String z  = String ( accelez);
        String x1 = String ( accele1x);
        String y1 = String ( accele1y);
        String z1 = String ( accele1z);

       delay(100); 

// Lora Transmit Data 
 
    
   
     //int DATA=100;
  String myValue;
  //String incFrame="123456789012345678901234567890123456789012345678901234567890";  //"000,32,54.4";
  String incFrame=  "G4"","+x+","+y+","+z+","+x1+","+y1+","+z1+","+v+","+lo+","+la+","+s+","+a;

  for(int i = 0; i < incFrame.length(); i++){
      myValue = myValue +  String(incFrame[i], HEX); 
    }
  SendString = "AAT2 Tx=1,uncnf,"+ myValue;
  Serial.println(SendString);
  Serial.print(sendLoRacmd(SendString,2000));
  delay(500);
  return 1; 
   }
}
}  

void LoRa_init()
{
  LoRa.begin(LoRaBaud);
}

void LoRa_WAN()
{
  Serial.println("Switch module to LORAWAN"); 
  SendString = "AAT1 LW=0";
  Serial.println("AAT1 LW=0");    
  Serial.print(sendLoRacmd(SendString ,2000));
   for (int ch=0;ch<8;ch++){ 
    SendString = "AAT2 Tx_Channel="+String(ch)+","+String(TxCh[ch])+",33,1,0";
    Serial.print(SendString);
    Serial.print(sendLoRacmd(SendString ,1000));
 }
 //for (int ch=0;ch<8;ch++){ 
 //   SendString = "AAT2 Tx_Channel="+String(ch+8)+","+String(TxCh[ch])+",30,1,0";
 //   Serial.print(SendString);
 //   Serial.print(sendLoRacmd(SendString ,1000));}
  
  SendString = "AAT2 JoinMode=0";
  Serial.println("AAT2 JoinMode=0");    
  Serial.print(sendLoRacmd(SendString ,1000));

  SendString = "AAT2 DutyCycle=0";
  Serial.println(SendString);   
  Serial.print(sendLoRacmd(SendString ,1000));
  
  SendString = "AAT2 Tx_Band=0,1,5";
  Serial.println(SendString);   
  Serial.print(sendLoRacmd(SendString ,1000));

  SendString = "AAT2 Rx2_Freq_DR=916100000,10";
  Serial.println(SendString);   
  Serial.print(sendLoRacmd(SendString ,1000));
  
  SendString = "AAT1 Save";
  Serial.println("AAT1 Save");    
  Serial.print(sendLoRacmd(SendString ,10000));
  SendString = "AAT1 Reset";
  Serial.println("AAT1 Reset");    
  Serial.print(sendLoRacmd(SendString ,5000));
  delay(5000);
}

String sendLoRacmd(String cmd, unsigned int Dutytime){
    String response = "";  // 接收LoRa回應值的變數  
    LoRa.println(cmd); // 送出LoRa命令到LoRa模組
    unsigned long timeout = Dutytime + millis();
    while (LoRa.available() || millis() < timeout) {
      while(LoRa.available()) {
      //  if(millis() > timeout) break;
        char c = LoRa.read(); // 接收LoRa傳入的字元
        response += c;
      }
   }

    //Serial.print(response);  // 顯示LoRa的回應
  return (response);
}


void LoRa_parameter()
{
  Serial.print("LoRa Firmware Version:");
  Serial.print( FW_version());
  
  Serial.print("Module Mode:");
  Serial.print(LoRa_Module_mode());
  
  SendString = "AAT2 ClassMode=?";
  Serial.print("LoRa ClassMode:");
  Serial.print(sendLoRacmd(SendString ,100));
    
  SendString = "AAT2 DevAddr=?";
  Serial.print("LoRa DevAddr=");  
  Serial.print(sendLoRacmd(SendString ,100));
  
  SendString = "AAT2 NwkSKey=?";
  Serial.print("LoRa NwkSKey=");    
  Serial.print(sendLoRacmd(SendString ,100));
  
  SendString = "AAT2 AppSKey=?";
  Serial.print("LoRa AppSKey=");  
  Serial.print(sendLoRacmd(SendString ,100));

  SendString = "AAT2 JoinMode=?";
  Serial.print("LoRa JoinMode=");  
  Serial.print(sendLoRacmd(SendString ,100));

 /*for (int ch=0;ch<8;ch++){ 
  //SendString = "AAT2 Tx_Channel"+String(ch)+"=?";  
  //Serial.print("LoRa Channel_"+String(ch)+"="); 
  //Serial.print(sendLoRacmd(SendString ,100));

    SendString = "AAT2 Tx_Channel="+String(ch)+","+String(TxCh[ch])+",30,1,0";
    Serial.print(SendString);
    Serial.print(sendLoRacmd(SendString ,100));
 }*/
}


String LoRa_Module_mode()
{
  SendString = "AAT1 LW=?";
  ReceiveString = sendLoRacmd(SendString ,100);
  return ReceiveString ;
}

String FW_version()
{
  SendString = "AAT1 FwVersion";
  ReceiveString = sendLoRacmd(SendString ,100);
  return ReceiveString ;
}
