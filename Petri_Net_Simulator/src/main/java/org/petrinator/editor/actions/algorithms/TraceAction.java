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

public class TraceAction extends JMenu {

    private Root root;
    private JMenuItem trace_menu;
    private static final String MODULE_NAME = "Trace export";

    private static String defaultLogDirectory = System.getProperty("user.home") + "/logs";
    private AbstractAction export_trace;
    private AbstractAction clean_file;


    public TraceAction(Root root){
        super(MODULE_NAME);
        Icon icon = new ImageIcon("pneditor/trace_export16.ico");
        this.setIcon(icon);
        this.setName(MODULE_NAME);
        this.root = root;
        createSubMenu();
    }



    private void createSubMenu()
    {
        this.add(new ExportTrace());
    }

    private class ExportTrace extends JMenuItem{

        private FileWriter file = null;
        private PrintWriter writer = null;

        public ExportTrace(){
            super("Export Trace");
            createWriter();
            this.setName("Export Trace");
            this.setIcon(new ImageIcon("pneditor/trace_export16.png"));
            this.addActionListener(new ActionListener() {
                @Override
                public void actionPerformed(ActionEvent e) {
                    try {
                        String transitionBuffer = SimulateAction.get_transitionBuffer();
                        writer.print(transitionBuffer); //Escribe los datos
                        writer.flush(); //El escritor cada vez que se cierra el txt se escribe sobre el mismo
                        SimulateAction.clean_transitionBuffer();
                    }catch(Exception err){
                        err.printStackTrace();
                    }
                }
            });
        }
        private void createWriter()
        {
            File dir = new File(defaultLogDirectory);
            if(!dir.exists()){
                dir.mkdirs();
            }
            file = null;
            try {
                file = new FileWriter(defaultLogDirectory + "/transitions.txt");
            } catch (IOException e) {
                e.printStackTrace();
            }
            writer = new PrintWriter(file);
        }
    }

}
