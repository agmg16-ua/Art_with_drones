package Nucleo;

import java.io.*;
import java.net.*;

import java.util.Properties;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

public class AD_Engine {

    //Con esta funcion enviare al dron la coordenada destino.
    //Orden en palabras: id_drone,coordenada_x,coordenada_y
    public static void enviarPorKafka(String [] palabras) {
    	// TODO Auto-generated method stub
		String servidoresBootstrap = "192.168.1.84:9092";
		String topic = "comunicacion";
		
		Properties props = new Properties();
		props.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, servidoresBootstrap);
		props.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		props.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		KafkaProducer<String, String> productor = new KafkaProducer<String, String>(props);
		try {
			productor.send(new ProducerRecord<String,String>(topic, "Mensaje?"));
			String mensaje = palabras[1] + " " + palabras[2] + " " + palabras[3];
			productor.send(new ProducerRecord<String,String>(topic,mensaje));
		} finally {
			productor.flush();
			productor.close();
		}
    }
    
    //Leo solamente una figura
    public static void leerFigura() {
    	File archivo = null;
        FileReader fr = null;
        BufferedReader br = null;
        String linea = "";
        
        try {
            // Apertura del fichero y creacion de BufferedReader para poder
            // hacer una lectura comoda (disponer del metodo readLine()).
        	archivo = new File ("figuras.txt");
            fr = new FileReader (archivo);
            br = new BufferedReader(fr);

            linea = br.readLine();
            
            char caracterAEliminar = '>'; // Carácter que deseamos eliminar
            
            //Leo hasta encontrar el final de la figura </figura>
            while((linea=br.readLine()).charAt(1) != '/'){
                String[] palabras = linea.split("<");
                
                //Elimino el caracter '>' ya que leo las palabras con el tambien y las paso por kafka al dron
                for(int i = 0;i<palabras.length;i++) {
                    // Usamos un bucle para construir el nuevo String sin el carácter a eliminar
                    StringBuilder nuevoTexto = new StringBuilder();
                    for (char c : palabras[i].toCharArray()) {
                        if (c != caracterAEliminar) {
                            nuevoTexto.append(c);
                        }
                    }

                    // Convertimos el StringBuilder de nuevo a String
                    palabras[i] = nuevoTexto.toString();
                }
                enviarPorKafka(palabras);
            }
        }
        catch(Exception e){
            e.printStackTrace();
        }finally{
            // En el finally cerramos el fichero, para asegurarnos
            // que se cierra tanto si todo va bien como si salta 
            // una excepcion.
            try{                    
                if( null != fr ){   
                	fr.close();     
                }                  
            }catch (Exception e2){ 
                e2.printStackTrace();
            }
        }
    }

    public static void main(String[] args) {
        String puerto = "";
        int maxDrones = 0;

        try{
            //if(args.length != 5) {
	          //  System.out.println("ERROR: Los parametros no son correctos");
	            //System.exit(1);
            //}
            
            leerFigura();
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
