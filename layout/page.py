def body_top():
    return '''<html>
   <head>
      <style>
      body {
      color: #00b300;
      background-color: #161716;
      }
      
      p {
      margin: 5px;
      }
      
              
        a:link {
          color: green;
          background-color: transparent;
          text-decoration: none;
        }
        a:visited {
          color: green;
          background-color: transparent;
          text-decoration: none;
        }
        a:hover {
          color: red;
          background-color: transparent;
          text-decoration: underline;
        }
        a:active {
          color: green;
          background-color: transparent;
          text-decoration: underline;
        }
        
        p:hover {
        color: red;
        }

      
      </style>
      
      <script type = "text/JavaScript">
         <!--
            function AutoRefresh( t ) {
               setTimeout("location.reload(true);", t);
            }
         //-->
      </script>
            
   </head>
   
   <body onload = "JavaScript:AutoRefresh(30000);" style="font: normal 14px Verdana, Arial, sans-serif; ">
 
 <p align="center"> Refresh in <span id="countdowntimer">30 </span> seconds</p>

<script type="text/javascript">
    var timeleft = 30;
    var downloadTimer = setInterval(function(){
    timeleft--;
    document.getElementById("countdowntimer").textContent = timeleft;
    if(timeleft <= 0)
        clearInterval(downloadTimer);
    },1000);
</script>

      '''


def body_bottom():
    return ''' </body>
   </html>
   '''
