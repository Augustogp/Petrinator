package org.petrinator.editor.actions.algorithms;

import com.google.gson.Gson;
import org.petrinator.editor.Root;
import org.petrinator.editor.actions.SimulateAction;
import org.petrinator.petrinet.Marking;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URLDecoder;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

public class TraceAction extends JMenu {

    private Root root;
    private JMenuItem trace_menu;
    private static final String MODULE_NAME = "Trace export";

    private static String defaultLogDirectory = System.getProperty("user.home") + "/logs";
    private static String defaultLogPath = defaultLogDirectory + "/transitions.txt";
    private static String defaultModulesPath = System.getProperty("user.dir") + "\\Petri_Net_Simulator\\Modulos\\Politics-generator";
    private AbstractAction export_trace;
    private AbstractAction clean_file;
    private ServerSocket sock_server;
    DataOutputStream out_stream = null;
    DataInputStream in_stream = null;


    public TraceAction(Root root){
        super(MODULE_NAME);
        Icon icon = new ImageIcon("pneditor/trace_export16.ico");
        this.setIcon(icon);
        this.setName(MODULE_NAME);
        this.root = root;
       // createSocket();
        createSubMenu();
    }

    private JMenuItem createFileRemover(){
        JMenuItem deleteTraceLog = new JMenuItem("Delete Trace Log");
        deleteTraceLog.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                try {
                    Files.deleteIfExists(Paths.get(defaultLogPath));
                } catch (IOException ioException) {
                    ioException.printStackTrace();
                }
            }
        });
        return deleteTraceLog;
    }

    private JMenuItem createStartComunnication(){
        JMenuItem startComunnication = new JMenuItem("Start Python Script");
        startComunnication.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                createSocket();
            }
        });
        return startComunnication;
    }

    private void redirectOutput(Process process) throws IOException {
        BufferedReader reader =
                new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder builder = new StringBuilder();
        String line = null;
        while ( (line = reader.readLine()) != null) {
            builder.append(line);
            builder.append(System.getProperty("line.separator"));
        }
        reader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
        line = null;
        while ( (line = reader.readLine()) != null) {
            builder.append(line);
            builder.append(System.getProperty("line.separator"));
        }
        String result = builder.toString();
        System.out.println("Resultados Python: " + result);
    }

    private void createSocket(){
        int port_server = 0;
        Socket sock_cli = null;

        try {
            sock_server = new ServerSocket(0);
            port_server = sock_server.getLocalPort();
        } catch (IOException e) {
            e.printStackTrace();
        }
        //        System.out.println("Path del jar " + get_Current_JarPath());

        System.out.println("Path del modulo es " + defaultModulesPath);
        String pathToPythonMain = defaultModulesPath + "/main_politics.py";
        System.out.println("Path del python " + pathToPythonMain);

        ProcessBuilder pb = new ProcessBuilder("python", pathToPythonMain, String.valueOf(port_server), SimulateAction.get_transitionBuffer(),generateJson());
        System.out.println("python" + pathToPythonMain + String.valueOf(port_server) + SimulateAction.get_transitionBuffer() + generateJson());
        try {
            Process process = pb.start();

            //Blocking accept executed python client
            sock_cli = sock_server.accept();
           // redirectOutput(process); //Print stdout and stderr of python in java

            out_stream = new DataOutputStream(sock_cli.getOutputStream());
            in_stream = new DataInputStream(sock_cli.getInputStream());
        } catch (IOException e) {
            e.printStackTrace();
        }

        return;
    }

    public String get_Current_JarPath()
    {
        String pathNet = SupervisionAction.class.getProtectionDomain().getCodeSource().getLocation().getPath();
        pathNet = pathNet.substring(0, pathNet.lastIndexOf("/"));
        if (System.getProperty("os.name").startsWith("Windows") && pathNet.startsWith("/"))
            pathNet = pathNet.substring(1, pathNet.length());
        String decodedPath = null;
        try {
            decodedPath = URLDecoder.decode(pathNet, "UTF-8");
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
        //System.out.println("Jar path : " + decodedPath);
        return decodedPath;
    }

    private String generateJson(){
        Map<String, Object> matrices = new HashMap<>();

        Gson gson = new Gson();

        matrices.put("I-", root.getDocument().getPetriNet().getBackwardsIMatrix());
        matrices.put("I+", root.getDocument().getPetriNet().getForwardIMatrix());
        matrices.put("Incidencia", root.getDocument().getPetriNet().getIncidenceMatrix());
        matrices.put("Inhibicion", root.getDocument().getPetriNet().getInhibitionMatrix());
        matrices.put("Marcado", root.getDocument().getPetriNet().getInitialMarking().getMarkingAsArray()[Marking.CURRENT]);

        String json = gson.toJson(matrices);
        return json.replace("\"", "\\\"");
    }

    private void createSubMenu()
    {
        this.add(new ExportTrace());
        this.add(createFileRemover());
        this.add(createStartComunnication());
    }

    private class ExportTrace extends JMenuItem{

        private FileWriter file = null;
        private PrintWriter writer = null;

        public ExportTrace(){
            super("Export Trace");
            this.setName("Export Trace");
            this.setIcon(new ImageIcon("pneditor/trace_export16.png"));
            this.addActionListener(new ActionListener() {
                @Override
                public void actionPerformed(ActionEvent e) {
                    try {
                        createWriter();
                        String transitionBuffer = SimulateAction.get_transitionBuffer();
                        writer.append(transitionBuffer);
                        writer.flush();
                        SimulateAction.clean_transitionBuffer();
                        writer.close();
                        file.close();
                    }catch(Exception err){
                        err.printStackTrace();
                    }

                }
            });
        }
        private void createWriter() throws IOException {
            File dir = new File(defaultLogDirectory);
            if(!dir.exists()){
                dir.mkdirs();
            }
            file = null;
            file = new FileWriter(defaultLogPath, true  );
            writer = new PrintWriter(file);

        }
    }

}
