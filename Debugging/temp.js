let i=0;
function fname()
{
    console.log(i);
    if(i==5)
        fx();
    i=i+1
}

let refreshIntervalId = setInterval(fname, 500);
function fx(){
    clearInterval(refreshIntervalId);
}

