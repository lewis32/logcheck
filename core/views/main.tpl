<html>
    <head>
    <title>日志匹配</title>
<!--     <link href="./css/template.css" rel="stylesheet" type="text/css" /> -->
    </head>
    <body>
        <div class="tab-content">
            <p><h2>日志匹配</h2></p>
            <ul id="tabs">
                <li class="current"><a href="#" title="tab1"></a>单条日志</li>
                <li><a href="#" title="tab2"></a>日志文件</li>
            </ul>
            <div id="content">
                <div id="tab1" ></div>
            </div>
            <form action="upload"method="POST" enctype="multipart/form-data">
                <input type="file"name="logfile" />
                <input type="submit"value="Upload" />
            </form>
        </div>
    </body>
    <!-- <script src="./js/template.js"></script> -->
</html>