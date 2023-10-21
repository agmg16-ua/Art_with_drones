package WeatherKafka;

import java.io.*;
import java.net.*;

/*
 * Necesitaremos crear un metodo para acceder a la base de datos y pasarle el resultado al Engine.
 * Nombre del método: climaActual().
 * Nombre variables: 
 *       lugar:  Dicha variable contiene la ciudad de la cual se pide el clima.
 *       temperatura: Contiene la temperatura del lugar.
 */
public class AD_Weather {

    private String lugar;
    private Double temperatura;

    //Lee los datos enviados por el AD_Engine, formato:"Clima en *lugar*", donde "lugar" es la información necesaria
    public String leerSocket(Socket socket,String datos){
        try
		{
			InputStream aux = socket.getInputStream();
			DataInputStream flujo = new DataInputStream(aux);
			datos = new String();
			datos = flujo.readUTF();
		}
		catch (Exception e)
		{
			System.out.println("Error: " + e.toString());
		}
        return datos;
    }

    /*
	* Escribe dato en el socket cliente. Devuelve numero de bytes escritos,
	* o -1 si hay error.
	*/
	public void escribeSocket (Socket p_sk, String p_Datos)
	{
		try
		{
			OutputStream aux = p_sk.getOutputStream();
			DataOutputStream flujo= new DataOutputStream( aux );
			flujo.writeUTF(p_Datos);      
		}
		catch (Exception e)
		{
			System.out.println("Error: " + e.toString());
		}
		return;
	}

    /*
        Funcion que actualizara temperatura dandole la temperatura de ese lugar.
        Esta funcion se encarga de acceder a la temperatura en la base de datos.
    */
    public void climaActual(){
        
    }

    //Como clima hace de servidor para engine hay que esperar hasta que lo llame
    public static void main(String[] args){
        String puerto = "";
        try{
            if(args.length < 1){
                System.out.println("Especifica el puerto de escucha");
                System.exit(1);
            }

            ServerSocket Ssocket = new ServerSocket(Integer.parseInt(puerto));

            while(true){
                Socket socket = Ssocket.accept();
                System.out.println("Esperando peticion...");

                AD_Weather clima = new AD_Weather();

                String peticion = new String();
                peticion = clima.leerSocket(socket,peticion);
                String[] palabras = peticion.split(" ");
                clima.lugar = palabras[2];
                clima.climaActual();

                clima.escribeSocket(socket, clima.temperatura.toString());
            }

        }
        catch(Exception e){
            System.out.println("Error: " + e.toString());
        }
    }
}
