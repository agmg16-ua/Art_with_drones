package Drones;

import java.io.*;
import java.net.*;
import java.util.Random;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;

public class AD_Drone {
    private String estado;  //En movimiento "Rojo" y en la posición final "Verde"
    private Integer[] posicion = new Integer[20]; //En el rando de 1 a 20
    private String alias; //Nombre_Drone
    private int id; //Id del drone
    private String verificado; //Orden dentro del programa

    //Constructor por defecto, cada dron empieza en la posicion (1,1) y en estado Rojo
    public AD_Drone(String alias){
        estado = "Rojo";
        posicion[0] = 0;
        posicion[1] = 0;
        this.alias = alias;
        Random random = new Random();
        id = random.nextInt(10000)+1;
        verificado = "";   
    }

    //Esta funcion sera la encargada de mover el dron. 
    //Si esta en la posicion final salgo y si llego a la posFinal cambio el estado a verde
    public void mover(Integer[] posicionFinal){
        if(estado == "Verde"){
            return;
        }

        if(posicionFinal[0] > posicion[0]){
            posicion[0]++;
        } 
        else if(posicionFinal[0] < posicion[0]){
            posicion[0]--;
        }

        if(posicionFinal[1] > posicion[1]){
            posicion[1]++;
        } 
        else if(posicionFinal[1] < posicion[1]){
            posicion[1]--;
        }

        if(posicionFinal[0] == posicion[0] && posicionFinal[1] == posicion[1]){
            estado = "Verde";
        }
    }

    //--------------------------------Parte como servidor---------------------------------------------------------

    //--------------------------------Parte como cliente----------------------------------------------------------    
    public void registrarse(String ip, String puerto) {
        try{
            String cadena = Integer.toString(this.id) + ' ' + this.alias;
            
            Socket skcliente = new Socket(ip, Integer.parseInt(puerto));
            
            OutputStream aux_ex = skcliente.getOutputStream();
			DataOutputStream flujo_exit= new DataOutputStream( aux_ex );
			flujo_exit.writeUTF(cadena);
            
            InputStream aux_in = skcliente.getInputStream();
            DataInputStream flujo_enter = new DataInputStream(aux_in);
            verificado = flujo_enter.readUTF();

            System.out.println("---Drone registrado de manera satisfactoria---" + "\n");

        }
        catch(Exception e) {
            System.out.println(e.toString());
            System.exit(-1);
        }
    }

    //-------------------------------------Inicio-----------------------------------------------------------------
    /**
	* @param args
	*/
    public static void main(String[] args) {
        if(args.length < 7) {
            System.out.println("ERROR: No hay suficientes argumentos");
            System.out.println("$./AD_Drone alias ip_Engine puerto_Engine ip_Kafka puerto_Kafka ip_Registry puerto_Registry");
            System.exit(-1);
        }

        AD_Drone drone = new AD_Drone(args[0]);

        String ip_Registry = args[5];
        String puerto_Registry = args[6];

        int opcion = -1;

        try {
            while(opcion != 3) {
                System.out.println("[1] Registrar drone en el sistema");
                System.out.println("[2] Entrar al espectaculo");
                System.out.println("[3] Salir");

                InputStreamReader isr = new InputStreamReader(System.in);
                BufferedReader br = new BufferedReader (isr);
                opcion = Integer.parseInt(br.readLine());

                if(opcion == 1) {
                    drone.registrarse(ip_Registry, puerto_Registry);
                }
                else if(opcion == 2) {

                }
                else {
                    System.exit(0);
                }
            }
        }
        catch (Exception e) {
            System.out.println(e.toString());
        }

    }
}


