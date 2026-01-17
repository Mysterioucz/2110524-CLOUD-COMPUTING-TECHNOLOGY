<?
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $file = '/tmp/sample-app.log';
    $message = file_get_contents('php://input');
    file_put_contents($file, date('Y-m-d H:i:s') . " Received message: " . $message . "\n", FILE_APPEND);
} else {
?>
    <!doctype html>
    <html lang="en">

    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>PHP Application - AWS Elastic Beanstalk</title>
        <meta name="viewport" content="width=device-width">
        <link rel="stylesheet" href="http://fonts.googleapis.com/css?family=Lobster+Two" type="text/css">
        <link rel="icon" href="https://awsmedia.s3.amazonaws.com/favicon.ico" type="image/ico">
        <link rel="shortcut icon" href="https://awsmedia.s3.amazonaws.com/favicon.ico" type="image/ico">
        <!--[if IE]><script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script><![endif]-->
        <link rel="stylesheet" href="/styles.css" type="text/css">
    </head>

    <body>
        <section class="congratulations">
            <h1>Congratulations!</h1>
            <p>Your AWS Elastic Beanstalk <em>PHP</em> application is now running on your own dedicated environment in the AWS&nbsp;Cloud</p>
            <p>You are running PHP version <?= phpversion() ?></p>

            <?php
            function matrixMultiply($A, $B)
            {
                $result = [];
                $rowsA = count($A);
                $colsA = count($A[0]);
                $colsB = count($B[0]);

                for ($i = 0; $i < $rowsA; $i++) {
                    for ($j = 0; $j < $colsB; $j++) {
                        $result[$i][$j] = 0;
                        for ($k = 0; $k < $colsA; $k++) {
                            $result[$i][$j] += $A[$i][$k] * $B[$k][$j];
                        }
                    }
                }
                return $result;
            }

            $size = 128;
            $A = [];
            $B = [];

            // Matrix seeding with random values
            for ($i = 0; $i < $size; $i++) {
                for ($j = 0; $j < $size; $j++) {
                    $A[$i][$j] = rand(1, 100);
                    $B[$i][$j] = rand(1, 100);
                }
            }

            $result = matrixMultiply($A, $B);
            echo "Matrix multiplication completed.\n";
            ?>

            <p>
                <!-- add mysql connection here -->
                <?php
                $conn = new mysqli(
                    "ip-172-31-13-169.ap-southeast-7.compute.internal",
                    "admin",
                    "123456",
                    "ebdb",
                );
                // Check connection
                if (mysqli_connect_errno()) {
                    echo "Failed to connect to MySQL: " .
                        mysqli_connect_error();
                    http_response_code(500);
                    exit();
                }

                $random = rand(0, 100000);
                $user = "'user" . $random . "'";
                $statement = $conn->prepare(
                    "INSERT into user (id, username) VALUES (?, ?)",
                );
                $statement->bind_param("is", $random, $user);
                $statement->execute();

                mysqli_close($conn);
                echo "Cloud Computing Auto Scaling<br>Engineered for Heavy Load: ";
                echo $random;
                ?>

            </p>


        </section>


        <section class="instructions">
            <h2>What's Next?</h2>
            <ul>
                <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/">AWS Elastic Beanstalk overview</a></li>
                <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/create_deploy_PHP_eb.html">Deploying AWS Elastic Beanstalk Applications in PHP Using Eb and Git</a></li>
                <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/create_deploy_PHP.rds.html">Using Amazon RDS with PHP</a>
                <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/customize-containers-ec2.html">Customizing the Software on EC2 Instances</a></li>
                <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/customize-containers-resources.html">Customizing Environment Resources</a></li>
            </ul>

            <h2>AWS SDK for PHP</h2>
            <ul>
                <li><a href="http://aws.amazon.com/sdkforphp">AWS SDK for PHP home</a></li>
                <li><a href="http://aws.amazon.com/php">PHP developer center</a></li>
                <li><a href="https://github.com/aws/aws-sdk-php">AWS SDK for PHP on GitHub</a></li>
            </ul>
        </section>

        <!--[if lt IE 9]><script src="http://css3-mediaqueries-js.googlecode.com/svn/trunk/css3-mediaqueries.js"></script><![endif]-->
    </body>

    </html>
<?
}
?>
 ?>
 ?>
 ?>
 ?>