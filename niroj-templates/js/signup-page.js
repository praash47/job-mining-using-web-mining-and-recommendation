var Form1=document.getElementById("Form1");
    var Form2=document.getElementById("Form2");
    var Form3=document.getElementById("Form3");

    var next1=document.getElementById("next1");
    var next2=document.getElementById("next2");
    var back1=document.getElementById("back1");
    var back2=document.getElementById("back2");
    
    var progress=document.getElementById("progress");

    next1.onclick=function(){
        Form1.style.left="-450px";
        Form2.style.left="40px";
        progress.style.width="240px";
    }

    back1.onclick=function(){
        Form1.style.left="40px";
        Form2.style.left="450px";
        progress.style.width="120px";   
    }

    next2.onclick=function(){
        Form2.style.left="-450px";
        Form3.style.left="40px";
        progress.style.width="360px";   
        
    }

    back2.onclick=function(){
        Form2.style.left="40px";
        Form3.style.left="450px";
        progress.style.width="240px";   
    }