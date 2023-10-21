package Nucleo;

import java.net.*;
import Drones.AD_Drone;
import java.util.Properties;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

public class AD_Engine {

    private AD_Drone[] drones;



    public static void main(String[] args) {
        String puerto = "";
        int maxDrones = 0;

        try{
            if(args.length != 5) {
            System.out.println("ERROR: Los parametros no son correctos");
            System.exit(1);
            }

            puerto = args[0];
            maxDrones = Integer.parseInt(args[1]);

            System.out.println("Escuchando puerto " + Integer.parseInt(puerto));
            System.out.println("Maximo de drones establecido en " + maxDrones + "drones");

            ServerSocket skEngine = new ServerSocket(Integer.parseInt(puerto));

            while(true) {
                Socket skDrone = skEngine.accept();
                System.out.println("Contactando drone...");

		        Thread t = new HiloServidor(skDrone);
                t.start();
            }

        } catch (Exception e) {
            System.out.println("Error" + e.toString());
        }

    }
}
