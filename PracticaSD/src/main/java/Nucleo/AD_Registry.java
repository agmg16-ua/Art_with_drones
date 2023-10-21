package Nucleo;

import java.net.*;
import java.io.*;
import java.util.UUID;

public class AD_Registry {
    public final String token = "Puedes entrar";
    public static int id_nueva = 1;
    public static String token_dron_actual = "";
    
    //Lee los datos enviados por el AD_Drones, formato:"ID Alias"
    public static String leerSocket(Socket socket,String datos){
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
    
    //Envia el token generado
	public static void enviarSocket(Socket p_sk,String token) {
		try
		{
			OutputStream aux = p_sk.getOutputStream();
			DataOutputStream flujo= new DataOutputStream( aux );
			flujo.writeUTF(token);      
		}
		catch (Exception e)
		{
			System.out.println("Error: " + e.toString());
		}
		return;
	}

    public static boolean existeEnBD(String id,String alias){
        File archivo = null;
        FileReader fr = null;
        BufferedReader br = null;
        String linea = "";
        boolean existe = false;
        
        try {
            // Apertura del fichero y creacion de BufferedReader para poder
            // hacer una lectura comoda (disponer del metodo readLine()).
            archivo = new File ("drones.txt");
            fr = new FileReader (archivo);
            br = new BufferedReader(fr);

            // Lectura del fichero
            while((linea=br.readLine())!=null){
                String[] palabras = linea.split(" ");
                if(palabras[0] == id){
                    existe = true;
                }
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
        return existe;
    }

    //Escribo en el fichero drones el nuevo dron, si ya existe no hago nada
    public static void escribirBD(String id,String alias){
        FileWriter fichero = null;
        PrintWriter pw = null;

        File archivo = null;
        
        try
        {
        	archivo = new File ("drones.txt");
            fichero = new FileWriter(archivo.getAbsoluteFile(), true);
            pw = new PrintWriter(fichero);

            if(existeEnBD(id, alias) != true){
                pw.write(token_dron_actual + " " + id + " " + id_nueva + " " + alias + "\n");
                id_nueva++;
            }

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
           try {
                if (null != fichero)
                    fichero.close();
           } catch (Exception e2) {
              e2.printStackTrace();
           }
        }
    }
    
    public static String generarToken() {
    	 // Genera un UUID aleatorio.
        UUID token = UUID.randomUUID();

        // Convierte el UUID en una cadena (string) si es necesario.
        String tokenString = token.toString();

        return tokenString;
    }

    public static void borrarFichero() {
    	try {
            // Abre el fichero en modo de escritura, lo que lo vaciará si ya contiene datos.
            FileWriter fos = new FileWriter("drones.txt");

            // Cierra el flujo directamente para así limpiarlo.
            fos.close();

            System.out.println("El fichero ha sido vaciado con éxito.");
        } catch (IOException e) {
            System.err.println("Error al vaciar el fichero: " + e.getMessage());
        }
    }
    
    public static void main(String[] args){
        try{
            if(args.length < 1){
                System.out.println("Faltan argumentos: <Puerto de escucha>");
                System.exit(-1);
            }
            String puerto = "";
            puerto = args[0];
            ServerSocket Ssocket = new ServerSocket(Integer.parseInt(puerto));
            
            borrarFichero();
            while(true){
                System.out.println("Esperando solicitud...");
                Socket socket = Ssocket.accept();
                 System.out.println("Recibida solicitud...");
                String peticion = "";
                peticion = leerSocket(socket,peticion);
                System.out.println(peticion);
                String[] palabras = peticion.split(" ");
                
                //Generacion del token
                token_dron_actual = generarToken();
                escribirBD(palabras[0],palabras[1]);
               
                enviarSocket(socket,token_dron_actual);
            }

        }
        catch(Exception e){
            System.out.println("Error: " + e.toString());
        }
    }
}
