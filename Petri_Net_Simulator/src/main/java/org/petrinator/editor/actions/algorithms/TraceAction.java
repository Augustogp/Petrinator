package org.petrinator.editor.actions.algorithms;

import com.google.gson.Gson;
import org.petrinator.editor.Root;
import org.petrinator.editor.actions.SimulateAction;
import org.petrinator.petrinet.Marking;
import org.petrinator.petrinet.Transition;
import pipe.utilities.math.Matrix;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URLDecoder;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

public class TraceAction extends JMenu {

    private Root root;
    private JMenuItem trace_menu;
    private static final String MODULE_NAME = "Trace export";

    private static String defaultLogDirectory = System.getProperty("user.home") + "/logs";
    private static String defaultLogPath = defaultLogDirectory + "\\transitions.txt";
    private static String defaultModulesPath = System.getProperty("user.dir") + "\\Petri_Net_Simulator\\Modulos\\Politics-generator";
    private AbstractAction export_trace;
    private AbstractAction clean_file;
    private ServerSocket sock_server;
    DataOutputStream out_stream = null;
    DataInputStream in_stream = null;
    Map<String,ArrayList<Integer>> TInvTraces;

    InvariantAction accion;



    public TraceAction(Root root){
        super(MODULE_NAME);
        accion = new InvariantAction(this.root);
        Icon icon = new ImageIcon("pneditor/trace_export16.ico");
        this.setIcon(icon);
        this.setName(MODULE_NAME);
        this.root = root;
       // createSocket();
        createSubMenu();
    }
    private void createSubMenu()
    {
        this.add(new ExportTrace());
        this.add(createFileRemover());
        this.add(createStartComunnication());
        this.add(createAux());
    }

    private JMenuItem createAux(){
        JMenuItem aux = new JMenuItem("Generate T Invariants");
        aux.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Es SRP3? " + isS3PR());
            }
        });
        return aux;
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
        String pathToPythonMain = defaultModulesPath + "\\main_politics.py";
        System.out.println("Path del python " + pathToPythonMain);
        ProcessBuilder pb = new ProcessBuilder("python", pathToPythonMain, String.valueOf(port_server), SimulateAction.get_transitionBuffer(), generateJsonMatrixStructure(),sendTInvTraces());
       // System.out.println("python" + pathToPythonMain + String.valueOf(port_server) + SimulateAction.get_transitionBuffer() + generateJsonMatrixStructure());
        try {
            Process process = pb.start();

            //Blocking accept executed python client
            sock_cli = sock_server.accept();
           redirectOutput(process); //Print stdout and stderr of python in java

            out_stream = new DataOutputStream(sock_cli.getOutputStream());
            in_stream = new DataInputStream(sock_cli.getInputStream());
        } catch (IOException e) {
            e.printStackTrace();
        }

        return;
    }

    private String sendTInvTraces(){
        String json = generateJson(TInvTraces);

        System.out.println("String json Tiv " + json);
        return json.replace("\"", "\\\"");
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

    private String generateJson(Map<String, ArrayList<Integer>> map){
        Gson gson = new Gson();
        String json = gson.toJson(map);
        return json;
    }

    private String generateJsonMatrixStructure(){
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

    //-------------------------------------------------------------------------------------------

    public boolean isS3PR()
    {
        System.out.println("----- Running S3PR Analysis -----\n");
        int[][] IncidenceMatrix = root.getDocument().getPetriNet().getIncidenceMatrix();
        Matrix TInvariants = accion.findVectors(new Matrix(root.getDocument().getPetriNet().getIncidenceMatrix()));
        TInvariants.transpose();
        System.out.println("There are "+ TInvariants.getColumnDimension()+ " T-invariants\n");

        if(!check_num_Tinvariants(TInvariants))return false;

        //creo un hashmap con las transiciones de los tinvariantes y las plazas de los t invariantes
        Map<String, ArrayList<Integer>> Tinvariants_trans = new LinkedHashMap<String,ArrayList<Integer>>();
        Map<String,ArrayList<Integer>> Tinvariants_places = new LinkedHashMap<String,ArrayList<Integer>>();
        Map<String,ArrayList<Integer>> Tinvariants_SM_places = new LinkedHashMap<String,ArrayList<Integer>>();
        TInvTraces = new LinkedHashMap<>();

        get_tinv_trans_and_places(IncidenceMatrix,TInvariants,Tinvariants_trans, Tinvariants_places);

        ArrayList<int[][]> Tinv_incidence_matrices = get_tinvariants_incidences_matrices(IncidenceMatrix, Tinvariants_trans, Tinvariants_places);

        print_hashmap(Tinvariants_trans,"T-Invariants Transitions");
        print_hashmap(Tinvariants_places,"T-Invariants Places");
        if(!check_closed_Tinvariants(Tinv_incidence_matrices,Tinvariants_trans,Tinvariants_places,Tinvariants_SM_places,TInvTraces))return false;
        //System.out.flush();
        //print_matrix(Tinv_incidence_matrices.get(0),"Incidence matrix of Tinv 1");
        //print_matrix(Tinv_incidence_matrices.get(1),"Incidence matrix of Tinv 2");

        Map<String,ArrayList<Integer>> Tinvariants_shared_places = get_shared_places(Tinvariants_places);
        print_hashmap(Tinvariants_shared_places,"T-Invariants Shared Places");
        print_arraylist(getEnabledTransitions(),"Enabled transitions");
        print_hashmap(Tinvariants_SM_places,"T-Invariants SM Places");
        print_hashmap(TInvTraces,"T-Invariants Transitions new");

        return true;
    }

    // ----------  S3PR CLASSIFICATION FUNCTIONS  ----------
    public boolean check_closed_Tinvariants(ArrayList<int[][]> Tinv_incidence_matrices,Map<String,ArrayList<Integer>> Tinvariants_trans,Map<String,ArrayList<Integer>> Tinvariants_places,Map<String,ArrayList<Integer>> Tinvariants_SM_place, Map<String,ArrayList<Integer>> traces)
    {
        System.out.println("----- Running T-Invariants SM Analysis -----\n");
        int cont = 1;
        ArrayList<Integer> Trans_Auxiliar = new ArrayList<Integer>();
        ArrayList<Integer> Places_Auxiliar = new ArrayList<Integer>();;
        int[][] Incidence_Auxiliar;
        for(int[][] matrices : Tinv_incidence_matrices)//recorremos las matrices de incidencia de los Tinvariantes
        {
            Trans_Auxiliar.clear();
            Places_Auxiliar.clear();
            Incidence_Auxiliar = matrices.clone();
            //print_matrix(Incidence_Auxiliar,"Incidence matrix of Tinv " + cont);
            int t,p,pAnterior;
            t=find_first_Tinvariants_enable_transition(Tinvariants_trans.get(String.format("TInv%d (T)",cont)));//aca iria la primer T sencibilizada sino 0;
            p=0;
            pAnterior=0;
            System.out.println("---------- Analyzing Tinv "+cont+" ----------");
            while (true) //p,t = f,c -> recorro Transiciones
            {
                p=0;
                while (Incidence_Auxiliar[p][t]!=1) //recorro las plazas de 1 transicion
                {
                    p++;
                    if(p==Incidence_Auxiliar.length)
                    {
                        System.out.println("El TInv "+ cont + "No es un State Machine\n");
                        return false;
                    }
                }
                if(!Trans_Auxiliar.contains(Tinvariants_trans.get(String.format("TInv%d (T)",cont)).get(t)))
                {
                    Trans_Auxiliar.add(Tinvariants_trans.get(String.format("TInv%d (T)",cont)).get(t));// guardo la transicion que ya se recorrio
                    System.out.println("Agrego al TInv "+cont +" La transicion: "+ Tinvariants_trans.get(String.format("TInv%d (T)",cont)).get(t));
                }
                else
                {
                    if((Trans_Auxiliar.get(0) == Tinvariants_trans.get(String.format("TInv%d (T)",cont)).get(t)) && (Trans_Auxiliar.containsAll(Tinvariants_trans.get(String.format("TInv%d (T)",cont)))))//si el bucle contiene todas las transiciones de t invariante
                    {
                        Tinvariants_SM_place.put(String.format("TInv%d (SMP)",(cont)), new ArrayList<Integer>(Places_Auxiliar));
                        System.out.println("El TInv "+ cont +" cumple las condiciones de SM\n");
                        break;//ya se cumplio las condiciones
                    }
                    else
                    {
                        if(!(Trans_Auxiliar.get(0) == Tinvariants_trans.get(String.format("TInv%d (T)",cont)).get(t)))
                            System.out.println("La transicion que se repitio no fue la primera");
                        if(!(Trans_Auxiliar.containsAll(Tinvariants_trans.get(String.format("TInv%d (T)",cont)))))
                            System.out.println("El bucle no paso por todas las Trasn del T invariante");
                        delete_place_arcs(Incidence_Auxiliar,pAnterior);//elimino los arcos de la plaza q me hizo el ciclo
                        t=find_first_Tinvariants_enable_transition(Tinvariants_trans.get(String.format("TInv%d (T)",cont)));//para q comience desde la t sencibilizada, sino 0
                        p=0;
                        pAnterior=0;
                        Trans_Auxiliar.clear();
                        Places_Auxiliar.clear();
                        System.out.println("Se encontro un recurso, Todavia no se determina si el TInv "+cont+" es un SM\n");
                        continue;
                    }
                }
                t=0;
                while (Incidence_Auxiliar[p][t]!=-1) //recorro las transiciones de plazas
                {
                    t++;
                    if(t==Incidence_Auxiliar[0].length)
                    {
                        System.out.println("el T invariante"+ String.format("TInv%d (T)",cont) + "Tiene una P que no tiene salida");
                        return false;
                    }
                }
                if(!Places_Auxiliar.contains(Tinvariants_places.get(String.format("TInv%d (P)",cont)).get(p)))
                {
                    Places_Auxiliar.add(Tinvariants_places.get(String.format("TInv%d (P)",cont)).get(p));//guardo la plaza que ya se recorrio
                    System.out.println("Agrego al TInv "+cont +" La plaza: "+Tinvariants_places.get(String.format("TInv%d (P)",cont)).get(p));
                }
                pAnterior=p;
            }
            traces.put(String.format(("TInv%d"),cont),new ArrayList<>(Trans_Auxiliar));
            cont++;
        }
        return true;
    }
    //find the index of the first enabled transition of a Tinvariant
    public int find_first_Tinvariants_enable_transition(ArrayList<Integer> Tinvariant_trans)
    {
        int index = 0;
        for(Integer trans : Tinvariant_trans)
        {
            if(getEnabledTransitions().contains(trans))
            {
                return index;
            }
            else
                index++;
        }
        return index;
    }
    // Verifies that there is more than one Closed Tinvariant, else return false (falta chequear q sean cerrados)
    public boolean check_num_Tinvariants(Matrix TInvariants)
    {
        if(TInvariants.getColumnDimension()<=1)
        {
            System.out.println("La red no es S3PR debido a: Existe 1 solo T invariante\n");
            return false;//existe un solo t invariante
        }
        else return true;
    }

    // Returns a hashmap of shared places between Tinvariants. (String Tinv -> arraylist of shared places )
    public Map<String,ArrayList<Integer>> get_shared_places(Map<String,ArrayList<Integer>> Tinvariants_places)
    {
        Map<String,ArrayList<Integer>> Tinvariants_shared_places = new LinkedHashMap<String,ArrayList<Integer>>();

        int Tinv_number = 1;
        for (ArrayList<Integer> places : Tinvariants_places.values())
        {
            Tinvariants_shared_places.put(String.format("TInv%d (SP)",(Tinv_number)), new ArrayList<Integer>());
            for (ArrayList<Integer> places_others : Tinvariants_places.values())
            {
                if(places.equals(places_others))
                    continue;

                add_intersection(places,places_others,Tinvariants_shared_places.get(String.format("TInv%d (SP)",(Tinv_number))));
            }
            Tinv_number ++ ;
        }
        return Tinvariants_shared_places;
    }
    public void add_intersection(ArrayList<Integer> list1,ArrayList<Integer> list2,ArrayList<Integer> list_dest)
    {
        for (Integer element : list1)
            if ( (list2.contains(element)) && (!list_dest.contains(element)))
                list_dest.add(element);
    }
    // Other S3PR3 associated functions


    // Obtains Tinvariants transition numbers (TinvN (T) -> [2,3,4,5]) and Tinvariants places numbers (TinvN (P) -> [1,2,5,7]) including shared and own places .
    public void get_tinv_trans_and_places(int [][]IncidenceMatrix,Matrix TInvariants,Map<String,ArrayList<Integer>> Tinvariants_trans,Map<String,ArrayList<Integer>> Tinvariants_places)
    {
        //1° agrego a los hashmap la cant de array list segun la cant de t invariantes
        for(int i=0;i<TInvariants.getColumnDimension();i++)
        {
            Tinvariants_places.put(String.format("TInv%d (P)",(i+1)), new ArrayList<Integer>());
            Tinvariants_trans.put(String.format("TInv%d (T)",(i+1)), new ArrayList<Integer>());
        }

        // ----- Obtención de las transiciones que componen los Tinvariantes
        for (int c=0; c < TInvariants.getColumnDimension(); c++)
        {
            for (int f=0; f < TInvariants.getRowDimension(); f++)
            {
                if(TInvariants.get(f,c)==1)
                {
                    Tinvariants_trans.get(String.format("TInv%d (T)",(c+1))).add((Integer)(f+1));
                }
            }
        }

        // ----- Obtención de las plazas de los Tinvariantes

        int suma,numarcos,Tinv_number=1;
        //1 recorro los arraylist de las transiciones por tivariante
        for (Map.Entry<String, ArrayList<Integer>> Tinv_trans : Tinvariants_trans.entrySet())
        {
            //2 recorro las plazas de la matriz de incidencia
            for (int f=0; f < IncidenceMatrix.length; f++)//plazas
            {
                suma=0;
                numarcos=0;
                for(int trans : Tinv_trans.getValue()) //itera por columna
                {
                    //verifico que sea un -1 o 1 para tener las plazas del t invariante
                    if(IncidenceMatrix[f][trans-1] == 1 || IncidenceMatrix[f][trans-1] == -1)
                        numarcos++;
                    suma += IncidenceMatrix[f][trans-1];
                }
                //aca verificas que tenga 2 o mas arcos opuestos para saber q sea una plaza del t invariante
                if((numarcos>=2) && (suma ==0))
                    Tinvariants_places.get(String.format("TInv%d (P)",(Tinv_number))).add((Integer)(f+1));
            }
            Tinv_number++;
        }
    }

    public ArrayList<int[][]> get_tinvariants_incidences_matrices(int [][]IncidenceMatrix,Map<String,ArrayList<Integer>> Tinvariants_trans,Map<String,ArrayList<Integer>> Tinvariants_places)
    {
        ArrayList<int[][]> Tinv_incidences = new ArrayList<int[][]>();
        for (int Tinv =0;Tinv<Tinvariants_trans.size();Tinv++)
        {
            // Get places and transitions of Tinvariant i .
            ArrayList<Integer> Tinv_trans = Tinvariants_trans.get(String.format("TInv%d (T)",(Tinv+1)));
            ArrayList<Integer> Tinv_places = Tinvariants_places.get(String.format("TInv%d (P)",(Tinv+1)));

            int [][] Tinv_incidence = new int[Tinv_places.size()][Tinv_trans.size()];

            for(int place_index=0;place_index<Tinv_places.size();place_index++)
            {
                int place = Tinv_places.get(place_index);

                for(int trans_index=0;trans_index<Tinv_trans.size();trans_index++)
                {
                    int transition = Tinv_trans.get(trans_index);
                    Tinv_incidence[place_index][trans_index] = IncidenceMatrix[place-1][transition-1];
                }
            }
            Tinv_incidences.add(Tinv_incidence);
        }
        return Tinv_incidences;

    }

    public ArrayList<Integer> getEnabledTransitions()
    {
        root.getDocument().getPetriNet().getInitialMarking().resetMarking();
        ArrayList<Transition> enabledArray = new ArrayList<Transition>(root.getDocument().getPetriNet().getInitialMarking().getAllEnabledTransitions());
        ArrayList<Integer> enabledNames= new ArrayList<Integer>();

        for (Transition transition : enabledArray)
        {
            enabledNames.add(Integer.valueOf(transition.getLabel().substring(1)));
        }
        return enabledNames;
    }
    public void delete_place_arcs(int[][] matrix,Integer row)
    {
        for (int c=0; c < matrix[0].length; c++)
        {
            matrix[row][c]=0;
        }

    }
    public void print_hashmap(Map<String,ArrayList<Integer>> hashmap,String Title)
    {
        System.out.println(Title);
        //iterate over the linked hashmap
        for (Map.Entry<String, ArrayList<Integer>> entry : hashmap.entrySet())
        {
            //Print key
            System.out.print(entry.getKey()+" : ");
            //Print value (arraylist)
            for(int list_element : entry.getValue()){
                System.out.print(list_element+" ");
            }
            System.out.println();
        }
        System.out.println();
    }

    public void print_arraylist(ArrayList<Integer> list,String Title)
    {
        System.out.println(Title);
        for(int list_element : list)
        {
            System.out.print(list_element+" ");
        }
        System.out.println();
    }

}
