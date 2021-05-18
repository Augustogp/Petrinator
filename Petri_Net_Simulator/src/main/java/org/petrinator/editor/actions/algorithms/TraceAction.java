package org.petrinator.editor.actions.algorithms;

import org.petrinator.editor.Root;
import org.petrinator.editor.actions.SimulateAction;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.nio.file.Files;
import java.nio.file.Paths;

public class TraceAction extends JMenu {

    private Root root;
    private JMenuItem trace_menu;
    private static final String MODULE_NAME = "Trace export";

    private static String defaultLogDirectory = System.getProperty("user.home") + "/logs";
    private static String defaultLogPath = defaultLogDirectory + "/transitions.txt";
    private AbstractAction export_trace;
    private AbstractAction clean_file;
    private ServerSocket sock_server;


    public TraceAction(Root root){
        super(MODULE_NAME);
        Icon icon = new ImageIcon("pneditor/trace_export16.ico");
        this.setIcon(icon);
        this.setName(MODULE_NAME);
        this.root = root;
      //  createSocket();
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
/*
    private void createSocket(){
        int port_server = 0;
        Socket sock_cli = null;

        try {
            sock_server = new ServerSocket(0);
            port_server = sock_server.getLocalPort();
        } catch (IOException e) {
            e.printStackTrace();
        }


    }
*/
    private void createSubMenu()
    {
        this.add(new ExportTrace());
        this.add(createFileRemover());
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
