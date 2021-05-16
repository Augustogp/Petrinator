package org.petrinator.auxiliar;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class TransitionsPrinter {

    private FileWriter file = null;
    private PrintWriter writer = null;

    private static String defaultLogDirectory = System.getProperty("user.home") + "/logs";

    public TransitionsPrinter(){
        try
        {
            File dir = new File(defaultLogDirectory);
            if(!dir.exists()){
                dir.mkdirs();
            }

            System.out.println("Llegue al constructor");
            file = new FileWriter(defaultLogDirectory + "/transitions.txt"); //Se crea un txt para escribir
            writer = new PrintWriter(file);//Se crea un escritor

        } catch(Exception e) {     //Si existe un problema cae aqui

            System.exit((1));
        }
    }
    public void writeFile(String data) throws IOException {
        try {
            writer.print(data); //Escribe los datos
            writer.flush(); //El escritor cada vez que se cierra el txt se escribe sobre el mismo
        }catch(Exception e){
            System.exit((1));
        }
    }
}
