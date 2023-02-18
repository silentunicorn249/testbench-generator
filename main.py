import random


def get_inputs_outputs(design):
        # split all statments ending in ;
        statements = design.split(';')
        # get first statement which is the module initialization
        moduleInitStatement = statements[0]
        # remove any redudent spaces
        moduleInitStatement = ' '.join(moduleInitStatement.split())
        # get ports area by getting the loc of the two parentheses
        portsArea = moduleInitStatement[moduleInitStatement.find('(') + 1: moduleInitStatement.find(')')].strip(" ")
        # array of ports
        ports = portsArea.split(",")

        inputs = []
        outputs = []

        # iterate over each port
        for port in ports:
            # split to port type(input, output) and any other type including reg or wire..
            portTypeAndName = port.strip(" ").split(" ")
            # port type(input, output)
            portType = portTypeAndName[0]
            # other data including port name and bit count if vector
            portName = portTypeAndName[1:]
            if portType == "input":
                inputs.append(' '.join(portTypeAndName[1:]))
            else:
                outputs.append(' '.join(portTypeAndName[1:]))
        return inputs, outputs


def init_inputs(inputs):
    s = ""
    for inp in inputs:
        inp = inp.replace("reg ", "").replace("wire ", "")
        if "clk" in inp:
            s+=f"{inp} = 1;\n"
            continue
        if "rst" in inp:
            s+=f"{inp} = 1;\n"
            continue
        if len(inp.split()) == 1:
            s+= f"{inp} = 0;\n"
        else:
            s+= f"{inp.split()[1]} = 0;\n"
    

    return s

def generate_tests(inputs, outputs):
    s=""
    for l in range(6):
        for inp in inputs:
            if 'clk' in inp:
                continue
            if 'rst' in inp:
                continue
            inp = inp.replace("reg", "").replace("wire", "")
            # print(inp)
            if len(inp.split()) == 1:
                bit = random.randrange(0,2)
                s+= f"#2 {inp} = 1'b{bit};\n"
            else:
                n = int(inp.split()[0][1])
                bits = ''
                for i in range(n):  
                    bits += str(random.randrange(0,2))
                s+= f"#2 {inp.split()[1]} = {n+1}'b{bits};\n"
        
        if(l==0):
            for out in outputs:
                if len(out.split()) > 1:
                    out = out.split()[-1]
                s+= f'$monitor("monitor value =%b" , {out});\n'
        s+= f'$display("Test case {l+1}"); \n'
        s+="#40;\n\n"

    return s


def generate_randoms(inputs):
    rst = extract_reset(extracted_inputs)
    s=''
    if rst:
        s+="rst=0;\nrst=1;\n"
    s+="for(i=0;i<1000000;i=i+1)\nbegin\n#40\n"
    for l in range(6):
        seed = random.choice(["seed1", "seed2", "seed3"])
        for inp in inputs:
            if 'clk' in inp:
                continue
            if 'rst' in inp:
                continue
            inp = inp.replace("reg ", "").replace("wire", "")
            if len(inp.split()) == 1:
                bit = random.randrange(0,2)
                s+= f"#2 {inp} = $random({seed});\n"
            else:
                n = int(inp.split()[0][1])
                bits = ''
                for i in range(n):  
                    bits += str(random.randrange(0,2))
                s+= f"#2 {inp.split()[1]} = $random({seed});\n"
            # s+= f"#2 {inp} = $random({seed});\n"
       
        s+="#40;\n\n"

    s+="end\n"
    
    return s
def generate_list(string: str, item):
    for line in string.split('\n'):
        if item in line:
            yield line

def parsed_instantiations(inputs):
    s = ""
    for inp in inputs:
        list1 = inp.split(" ")
        inputName = list1[len(list1)-1]
        s+= f"        .{inputName}({inputName}),\n"
    s = s[0:len(s)-2]
    return s
 

def extract_clock(inputs):
    for inp in inputs:
        if "clk" in inp:
            #return "always #5 clk = !clck;"
            return """
initial 
    begin
    clk = 0;
    forever begin
    #5;
    clk = ~clk;

    end
end
            """
    return ""

def extract_reset(inputs):
    for inp in inputs:
        if "rst" in inp:
            return "#10 rst = 1;\n"
    return ""

def parsed_inputs(inputs):
    s = ""
    for inp in inputs:
        replacedStr = inp.replace("reg ", "").replace("wire", "")
        s+= f"reg {replacedStr};\n"
 
    return s
def parsed_outputs(outputs):
    s = ""
    for inp in outputs:
        replacedStr = inp.replace("reg ", "").replace("wire", "")
        s+= f"wire {replacedStr};\n"
 
    return s

def main ():
    x = input("Enter file name: ")
    design = open(x).read()

    module_name = design.split()[1]

    extracted_inputs, extracted_outputs = get_inputs_outputs(design)
    clk = extract_clock(extracted_inputs)
    rst = extract_reset(extracted_inputs)
    test_inputs = parsed_inputs(extracted_inputs)

    test_outputs = parsed_outputs(extracted_outputs)

    dut = parsed_instantiations(extracted_inputs+extracted_outputs)

    inital = init_inputs(extracted_inputs)
    tests = generate_tests(extracted_inputs, extracted_outputs)
    randoms = generate_randoms(extracted_inputs)


    out = f"""module {module_name}_tb ();
    {test_inputs}
    {test_outputs}

    {module_name} DUT (
    {dut}
        );

    integer seed1=10;
    integer seed2=20;
    integer seed3=30;
    integer i=0;

    {clk}

    initial
        begin
        $dumpfile("{module_name}.vcd");
        $dumpvars ;

    //initial values
    {inital}

        #40;
    {tests}
    {randoms}
    {"rst = 0;" if rst else ""}
        #100;
        $finish();
        end



    endmodule
    """

    output_file = open(module_name+"_tb.v", "w+").write(out)

main()