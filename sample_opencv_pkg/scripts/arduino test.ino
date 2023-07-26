unsigned long start_time;
unsigned long stop_time;
unsigned int values[100];
unsigned int i;
byte sendValue = 0xFF;
byte returnValue = 0;

void setup()
   {        
    Serial.begin(115200);  
    //analogReadResolution(8);
    ADC->ADC_MR = 0x10380080;              // change from 10380200 to 10380080, 0 is the PRESCALER and 8 means FREERUN
    ADC->ADC_CHER = 3;
    ADC->ADC_CR = 2;                       // START
    Serial.print("frequency reading:");
    sendValue = 0x64;
    Serial.println(sendValue);
    returnValue = Serial.print(sendValue);     // transmit data 
    //ADC -> ADC_CHER = 0x03;                 // enable ADC on pin A7
   }

void loop()
{
    start_time = micros();
    for(i = 0; i < 100; i++)
    {
        while((ADC->ADC_ISR & 0x03)==0);  // wait for conversion
        values[i] = ADC->ADC_CDR[0];      //get values
    }  
    //delay(5);
    
    stop_time = micros();

    Serial.print("Total time for 100 values: ");
    Serial.print(stop_time-start_time);
    Serial.println(" microseconds");
    Serial.print("Average time in microseconds per conversion: ");
    Serial.println((float)(stop_time-start_time)/100);
    Serial.println("Values: ");
    
    for(i=0;i<100;i++)
    {
        Serial.println(values[i]);
    }
    
    delay(2000);
}

   