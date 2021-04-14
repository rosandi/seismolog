/* 
  Instrumentation apps
  YRAPP
*/

const ww= window.innerWidth;
const wh= window.innerHeight;

var runid;
var running=false;
var msrlen=100;
var avg=10;
var dt=1;
var chn=1;

var pline = [{x: [0],y: [0],type: 'scatter',name: 'V1'}, 
             {x: [0],y: [0],type: 'scatter',name: 'V2'},
             {x: [0],y: [0],type: 'scatter',name: 'V3'}];

plotwidth=0.55*ww;
plotheight=0.3*wh;

var layoutx = {
  width: plotwidth,
  height: plotheight,
  autosize: false,
  margin: {
    l: 50,
    r: 50,
    b: 50,
    t: 40,
    pad: 4
  },
  yaxis: {range: [-200, 200],autorange: true,title: 'X (a.u.)'},
  xaxis: {title: 'time (s)'}
};

var layouty = {
  width: plotwidth,
  height: plotheight,
  autosize: false,
  margin: {
    l: 50,
    r: 50,
    b: 50,
    t: 40,
    pad: 4
  },
  yaxis: {range: [-200, 200],autorange: true,title: 'Y (a.u.)'},
  xaxis: {title: 'time (s)'}
};

var layoutz = {
  width: plotwidth,
  height: plotheight,
  autosize: false,
  margin: {
    l: 50,
    r: 50,
    b: 50,
    t: 40,
    pad: 4
  },
  yaxis: {range: [-200, 200],autorange: true,title: 'Z (a.u.)'},
  xaxis: {title: 'time (s)'}
};

var plotdatax=[pline[0]];
var plotdatay=[pline[1]];
var plotdataz=[pline[2]];

Plotly.newPlot('plotareax',plotdatax,layoutx);
Plotly.newPlot('plotareay',plotdatay,layouty);
Plotly.newPlot('plotareaz',plotdataz,layoutz);

function getval(elid) {
    return document.getElementById(elid).value;
}

function setval(elid,val) {
    document.getElementById(elid).value=val;
}

function getstatus() {
    $.getJSON('status', function(stat) {
        if(stat.status) {
            $('#statustext').append('Logging daemon is <strong>running</strong><br>');
        } else {
            $('#statustext').append('Logging daemon is <strong>not running</strong><br>');
        }
        ss='Uptime: '+stat.uptime+'<br>Storage:<br>'
        sh=stat.disk[0].replace(/\s+/g, ' ').trim().split(' ');
        sc=stat.disk[1].replace(/\s+/g, ' ').trim().split(' ');
        dtab='<table style="width:13em"><tr><th class="noborder">'+sh[0]+
              '</th><th class="noborder">'+sh[1]+
             '</th><th class="noborder">'+sh[2]+
             '</th><th class="noborder">'+sh[3]+
             '</th></tr>';

        dtab+='<tr><td class="noborder">'+sc[0]+
              '</td><td class="noborder">'+sc[1]+
              '</td><td class="noborder">'+sc[2]+
              '</td><td class="noborder">'+sc[3]+
              '</td></tr></table>';
        
        $('#statustext').append(ss+dtab);
        $.getJSON('list/json/count', function(s){
            $('#statustext').append('Recorded data: '+s.count+'<br>');
        });
    });
    $('#statustext').scrollTop = $('#statustext').scrollHeight - $('#statustext').clientHeight;
}

function shutdown() {
    $("#statustext").html("<div style='text-align:center'>system shutdown...<br><H1>GOOD BYE...</H1></div>");
    $.getJSON("shutdown",function(st){});
}

function togglerun() {
    $.getJSON('status',
    function(stat){
        if(stat.status) {
            $.getJSON('stop',function(s){
                console.log('stopping');
                $('#runbtn').css({'background-color':'green'});
                $('#runbtn').html('START');
                var d=new Date();
                sdate='stop: '+d.getDate()+'-'+(d.getMonth()+1)+'-'+d.getFullYear();
                sdate+=' '+d.getHours()+':'+d.getMinutes()+':'+d.getSeconds()+'<br>';
                $('#statustext').append('<strong>'+sdate+'</strong>')
            });
        } else {
            $.getJSON('start',function(s){
                console.log('starting');
                $('#runbtn').css({'background-color':'red'});
                $('#runbtn').html('STOP');
                var d=new Date();
                sdate='start logging at: '+d.getDate()+'-'+(d.getMonth()+1)+'-'+d.getFullYear();
                sdate+=' '+d.getHours()+':'+d.getMinutes()+':'+d.getSeconds()+'<br>';
                $('#statustext').append('<strong>'+sdate+'</strong>');
                $('#statustext').append(s.program+'<br>');
            });
        }
    });
}

function listFiles(){
    $.getJSON('list/json',function(lst) {
        s='';
        for(i=0;i<lst.files.length;i++) {
            fl=lst.files[i].replace(/.json/,'')
            s+='<tr><td class="cell" onclick=plotfile($(this).html()+".json")>'+fl+'</td></tr>';
        }
        $('#filelist').html(s);
    });
}

function plotfile(fname) {
    if(fname=='--' || fname=='' || fname=='null') return;
    $.getJSON('load/'+fname, function(data){
        t=new Array(data.length);
        dt=data.tsample/data.length;
        for (i=0;i<data.length;i++) {
            t[i]=i*dt;
        }
        
        layoutx.xaxis={range: [0,data.tsample],title: 'time (s)'};
        layouty.xaxis={range: [0,data.tsample],title: 'time (s)'};
        layoutz.xaxis={range: [0,data.tsample],title: 'time (s)'};
        
        pline[0].x=t;
        pline[1].x=t;
        pline[2].x=t;
        
        pline[0].y=data.x;
        pline[1].y=data.y;
        pline[2].y=data.z;
        Plotly.redraw('plotareax');
        Plotly.redraw('plotareay');
        Plotly.redraw('plotareaz');
        $('#display').html('FILE: '+fname.replace(/.json/,''));
    });
}

function sendcmd() {
    cmd=getval('cmdtext').replace(/ /g,'/');
    console.log(cmd);
    $.get(cmd,function(data){
        $('#longresponse').append(data+'<br>');
    });
}

function apply() {
    msrlen=getval('len');
    avg=getval('avg');
    dt=getval('dt');
    chn=0;
    if(document.getElementById('ch1').checked) chn+=1;
    if(document.getElementById('ch2').checked) chn+=2;
    if(document.getElementById('ch3').checked) chn+=4;

    if(chn==0) {
        chn=1; // avoids nonsense
        document.getElementById('ch1').checked=true;
    }
    
    sconf='par/chanmask='+chn+':block='+msrlen+':avg='+avg+':delay='+dt+'/';
    $.get(sconf,function(resp){
        $('#longresponse').append(resp+'<br>');
    });
}

// Called on load
$.getJSON('status', function(s) {
    if(s.status) {
        $('#runbtn').css({'background-color':'red'});
        $('#runbtn').html('STOP');
        $.getJSON('get/settings', function(st){
            $('#longresponse').html('Device settings:<br>'+JSON.stringify(st)+'<br>');
            $('#len').val(st.block);
            $('#v_len').html(st.block);
            // ... and here comes other settings
        });
    } else {
        dd=new Date();
        // Javascript starts month at 0 (January), funny heh?
        sd =dd.getFullYear()+'-'+(dd.getMonth()+1)+'-'+dd.getDate()+'+';
        sd+=dd.getHours()+':'+dd.getMinutes()+':'+dd.getSeconds();
        $.get('set/date='+sd,function(rs) {
            $('#statustext').html(rs+'<br>');
        });
    }
});
