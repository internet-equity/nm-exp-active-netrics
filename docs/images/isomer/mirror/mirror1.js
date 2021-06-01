var Point  = Isomer.Point;
var Path   = Isomer.Path;
var Shape  = Isomer.Shape;
var Vector = Isomer.Vector;
var Color  = Isomer.Color;

var iso = new Isomer(document.getElementById("canvas"));

var red = new Color(160, 60, 50);
var blue = new Color(80, 90, 160);
var bluey = new Color(20, 70, 90);
var bluey2 = new Color(10, 50, 90);
var gray = new Color(40, 40, 40);
var green = new Color(0, 255, 0);
var greeny = new Color(10, 255, 10);
var yellow = new Color(255, 190, 0);
var yellow2 = new Color(255, 190, 0);
var black = new Color(0, 0, 0);
var lgray = new Color(180, 180, 180);
var llgray = new Color(80, 80, 80);
var white = new Color(250, 250, 250);

//eth cable
//iso.add(Shape.Prism(Point(8.6, 1.0, 1.1), 0.1, 3.2, .1), blue);
//iso.add(Shape.Prism(Point(3.1, 6.2, 1.35), 0.4, .4, .35), black);
//iso.add(Shape.Prism(Point(3.3, 6.1, 1.1), 0.5, .4, .4), blue)
//iso.add(Shape.Prism(Point(3.6, 4.1, 1.1), 0.1, 2.1, .1), blue);
//iso.add(Shape.Prism(Point(3.6, 4.1, 1.1), 5.0, .1, .1), blue);
//iso.add(Shape.Prism(Point(8.0, 1.0, 1.1), 0.6, .1, .1), blue);
//iso.add(Shape.Prism(Point(7.3, 0.8, 1.1), 0.5, .5, .4), blue);
//iso.add(Shape.Prism(Point(6.75, 0.62, 1.36), 0.3, .36, .35), black);

//rpi
//iso.add(Shape.Prism(Point(-3, 1.5, 7), 2, 3, 0.8));
//iso.add(Shape.Prism(Point(3.5,7.8,0.8), 0.73, 0.1, 0.5), gray);
//iso.add(Shape.Prism(Point(4.4,7.8,1.1), 0.4, 0.1, 0.2), gray);
//iso.add(Shape.Prism(Point(4.4,7.8,0.8), 0.4, 0.1, 0.2), gray);
//iso.add(Shape.Prism(Point(4.9,7.8,0.8), 0.4, 0.1, 0.2), gray);
//iso.add(Shape.Prism(Point(4.9,7.8,1.1), 0.4, 0.1, 0.2), gray);
//iso.add(Shape.Prism(Point(4.0,7.8,0.82), 0.12, 0.0, 0.1), green);
//iso.add(Shape.Prism(Point(3.65,7.8,0.82), 0.12, 0.0, 0.1), yellow);
//iso.add(Shape.Prism(Point(3.6,7.8,0.95), 0.53, 0, 0.3), black);
//iso.add(Shape.Prism(Point(2.9,8.8,1.2), 0.1, 0.4, 0.2), gray);
//iso.add(Shape.Prism(Point(2.9,9.9,1.2), 0.1, 0.3, 0.1), gray);

//switch
/*iso.add(Shape.Prism(Point(-3, 1.5, 7), 3, 5, 0.8));
iso.add(Shape.Prism(Point(3.2,7.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,8.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,8.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,7.9,1.1), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,8.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,9.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,9.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,8.9,1.1), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,9.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,10.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,10.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,9.9,1.1), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,10.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,11.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,11.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,10.9,1.1), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,11.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,12.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,12.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,11.9,1.1), 0.0, 0.53, 0.3), black);*/

iso.add(Shape.Prism(Point(-3, 1.5, 7), 3.1, 4.1, 0.8));

iso.add(Shape.Prism(Point(3.2,11.1,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,11.2,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,11.6,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.2,11.2,1.0), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,10.3,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,10.4,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,10.8,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.2,10.4,1.0), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,9.5,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,9.6,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,10,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.2,9.55,1.0), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,8.7,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,8.8,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,9.2,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.2,8.75,1.0), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,7.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,8.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,8.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,7.9,1.1), 0.0, 0.53, 0.3), black);

//eth1
iso.add(Shape.Prism(Point(9.3, 5.8, 1.36), .3, .36, .35), black);
iso.add(Shape.Prism(Point(8.6, 5.6, 1.5), 0.5, .5, .4), yellow);
iso.add(Shape.Prism(Point(1, 6.5, 0.95), 8.3, .1, .1), yellow);

iso.add(Shape.Prism(Point(1.7,8.3, 1.36), .3, .36, .35), black);
iso.add(Shape.Prism(Point(1.0, 8.1, 1.5), 0.5, .5, .4), yellow);
iso.add(Shape.Prism(Point(0.85, 8.9, 1.1), 0.70, .1, .1), yellow);
iso.add(Shape.Prism(Point(1, 6.6, 0.95), .1, 2.5, .1), yellow);

iso.add(Shape.Prism(Point(1.7,10, 1.36), .3, .36, .35), black);
iso.add(Shape.Prism(Point(1.0, 9.8, 1.5), 0.5, .5, .4), greeny);
iso.add(Shape.Prism(Point(-1.0, 10.5, 1.1), 2.5, .1, .1), greeny);

iso.add(Shape.Prism(Point(-1, -2.3, 0.99), .1, 13, .1), greeny);

iso.add(Shape.Prism(Point(8.5, 12.5, 1.1), .1, .1, 1), blue);

iso.add(Shape.Prism(Point(1.7,11, 1.36), .3, .36, .35), black);
iso.add(Shape.Prism(Point(1.0, 10.8, 1.5), 0.5, .5, .4), blue);
iso.add(Shape.Prism(Point(0.5, 11.5, 1.1), 1, .1, .1), blue);
iso.add(Shape.Prism(Point(0.5, 12.5, 1.1), 8, .1, .1), blue);

iso.add(Shape.Prism(Point(0.5, 11.5, 1.1), .1, 1, .1), blue);


iso.add(Shape.Prism(Point(8.5, 11.5, 2), .1, 1, .1), blue);

iso.add(Shape.Prism(Point(3, 2.5, 6), 1.4, 4.1, 3.8), llgray);





/*
iso.add(Shape.Prism(Point(3.2,8.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,9.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,9.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,8.9,1.1), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,9.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,10.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,10.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,9.9,1.1), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,10.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,11.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,11.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,10.9,1.1), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,11.9,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,12.0,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,12.4,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,11.9,1.1), 0.0, 0.53, 0.3), black);

iso.add(Shape.Prism(Point(3.2,8.3,0.9), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(3.2,8.3,0.9), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(3.2,8.7,0.9), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(3.1,8.2,1.1), 0.0, 0.53, 0.3), black);
*/
//iso.add(Shape.Prism(Point(3.9,9.95,1.2), 1.4, 0.0, 0.16), gray);
//iso.add(Shape.Prism(Point(3.9,10.2,1.2), 1.4, 0.0, 0.2), gray);
//iso.add(Shape.Prism(Point(3.9,10.45,1.2), 1.4, 0.0, 0.2), gray);

//iso.add(Shape.Prism(Point(3.9,9.7,1.2), 1.4, 0.0, 0.16), gray);
//iso.add(Shape.Prism(Point(3.9,9.45,1.2), 1.4, 0.0, 0.2), gray);
//iso.add(Shape.Prism(Point(3.9,9.2,1.2), 1.4, 0.0, 0.2), gray);

//mini usb
//iso.add(Shape.Prism(Point(8.5,12.05,1.0), 0.3,0.10, 0.45), lgray);
//iso.add(Shape.Prism(Point(8.63,12.05,1.05), 0.05,0.00, 0.10), black);
//iso.add(Shape.Prism(Point(8.63,12.05,1.2), 0.05,0.00, 0.10), black);
//iso.add(Shape.Prism(Point(8.2,12.0,1.0), 0.3,0.25, 0.45), llgray);
//iso.add(Shape.Prism(Point(2.4,9.9,1.2), 0.2, 0.28, 0.05), lgray);
//iso.add(Shape.Prism(Point(2.2,9.9,1.16), 0.2, 0.32, 0.1), llgray);
//iso.add(Shape.Prism(Point(1.2,9.95,1.16), 0.96, 0.2, 0.08), llgray);
//iso.add(Shape.Prism(Point(1.2,11.95,1.16), 6.96, 0.2, 0.08), llgray);
//iso.add(Shape.Prism(Point(1.2,9.95,1.16), 0.2,2.2, 0.08), llgray);

//usb charger
//iso.add(Shape.Prism(Point(10.6,12.05,1.3), 0.32,0.05, 0.2), lgray);
//iso.add(Shape.Prism(Point(10.6,12.30,1.3), 0.32,0.05, 0.2), lgray);
//iso.add(Shape.Prism(Point(10.35,12.0,1.2), 0.2,0.5, .55), llgray);

//iso.add(Shape.Prism(Point(10.0,12.0,.45), 0.3,0.6, 1.3), llgray);
//iso.add(Shape.Prism(Point(10.0,12.2,0.7), 0.1, 0.2, 0.4), gray);
//iso.add(Shape.Prism(Point(10.0,12.2,1.5), 0.0, 0.1, 0.1), red);

//power outlet
//iso.add(Shape.Prism(Point(13.35,10.0,0), 0,2, 3.55), lgray);
//iso.add(Shape.Prism(Point(13.35,10.3,0.5), 0.02,1.5, 2.55), white);

//iso.add(Shape.Prism(Point(13.35,10.4,1.6), 0.02,1.3, 0.1), lgray);

//iso.add(Shape.Prism(Point(13.35,10.6,2.), 0.0,.8, 0.65), lgray);
//iso.add(Shape.Prism(Point(13.35,10.8,2.3), 0.0,.05, 0.2), black);
//iso.add(Shape.Prism(Point(13.35,11.1,2.3), 0.0,.05, 0.2), black);
//iso.add(Shape.Prism(Point(13.35,10.95,2.1), 0.0,.05, 0.1), black);


//router
iso.add(Shape.Prism(Point(6,-5,1), 1.0, 7, 1));
iso.add(Shape.Prism(Point(5, -4.5, 1), 1, 6, 0.8));
iso.add(Shape.Prism(Point(4, -5, 1), 1.5, 7, 1));
iso.add(Shape.Prism(Point(1, -6.5, 3), 1, 6, 0.8));
iso.add(Shape.Prism(Point(2, -5, 1), 1.5, 7, 1));
iso.add(Shape.Prism(Point(2.0,-4.0,1.2), 0.0, 0.5, .4), yellow);
iso.add(Shape.Prism(Point(2.0,-3.4,1.2), 0.0, 0.5, .4), yellow);
iso.add(Shape.Prism(Point(2.0,-2.8,1.2), 0.0, 0.5, .4), yellow);
iso.add(Shape.Prism(Point(2.0,-2.2,1.2), 0.0, 0.5, .4), yellow);
iso.add(Shape.Prism(Point(2.0,-1,1.2), 0.0, 0.5, .4), bluey2);
iso.add(Shape.Prism(Point(2.0,-3.9, 1.25), 0.0, 0.3, .3), black);
iso.add(Shape.Prism(Point(2.0,-3.3, 1.25), 0.0, 0.3, .3), black);
iso.add(Shape.Prism(Point(2.0,-2.7, 1.25), 0.0, 0.3, .3), black);
iso.add(Shape.Prism(Point(2.0,-2.1, 1.25), 0.0, 0.3, .3), black);
iso.add(Shape.Prism(Point(2.0,-0.9, 1.25), 0.0, 0.3, .3), black);

iso.add(Shape.Prism(Point(1.8,1.9,1.10), 0.6, 0.2, 0.15), black);
iso.add(Shape.Prism(Point(1.8,1.9,1.10), 0.2, 0.2, 3.15), black);

iso.add(Shape.Prism(Point(1.8,-1.2,1.10), 0.6, 0.2, 0.15), black);
iso.add(Shape.Prism(Point(1.8,-1.2,1.10), 0.2, 0.2, 3.15), black);

iso.add(Shape.Prism(Point(1.8,-4.2,1.10), 0.6, 0.2, 0.15), black);
iso.add(Shape.Prism(Point(1.8,-4.2,1.10), 0.2, 0.2, 3.15), black);

//eth internet
/*iso.add(Shape.Prism(Point(0.5, -2.1, 1.36), .3, .36, .35), black);
iso.add(Shape.Prism(Point(-0.2, -2.3, 1.5), 0.5, .5, .4), yellow);
iso.add(Shape.Prism(Point(-0.7, -1.6, 1.1), 1.0, .1, .1), yellow);
*/
iso.add(Shape.Prism(Point(0.5, -3.0, 1.36), .3, .36, .35), black);
iso.add(Shape.Prism(Point(-0.2, -3.2, 1.5), 0.5, .5, .4), greeny);
iso.add(Shape.Prism(Point(-1.1, -2.5, 1.1), 1.35, .1, .1), greeny);

//iso.add(Shape.Prism(Point(-0.8, 5.1, 1.0), 0.4, .4, .35), black);
//iso.add(Shape.Prism(Point(-.9, 4.7, 1.0), 0.5, .4, .4), yellow)
//iso.add(Shape.Prism(Point(-0.7, -1.5, 1.1), 0.1, 6.5, .1), yellow);

//iso.add(Shape.Prism(Point(0.6, 4.1, 1.1), 0.1, 2.1, .1), blue);



//iso.add(Shape.Prism(Point(9.6, -2.6, 1.1), 0.1, 9.2, .1), yellow);
//iso.add(Shape.Prism(Point(8.0, -2.6, 1.1), 1.6, .1, .1), yellow);
//iso.add(Shape.Prism(Point(7.3, -2.8, 1.1), 0.5, .5, .4), yellow);
//iso.add(Shape.Prism(Point(6.75, -3.0, 1.36), 0.3, .36, .35), black);
//dongle
/*iso.add(Shape.Prism(Point(10.4,5.4,0.45), .35, 0.45, 0.11), lgray);
iso.add(Shape.Prism(Point(9.8,5.4,0.4), .6, 0.58, 0.18), llgray);
iso.add(Shape.Prism(Point(8.2,5.6,0.4), 1.6, 0.18, 0.18), llgray);
iso.add(Shape.Prism(Point(5.9,4.8,0.8), 1.6, 0.7, 0.5), llgray);
//iso.add(Shape.Prism(Point(7.9,4.8,0.8), 1.6, 0.7, 0.5), llgray);
iso.add(Shape.Prism(Point(10.6,5.80,0.46), 0.1,0.10, 0.0), black);
iso.add(Shape.Prism(Point(10.6,5.6,0.46), 0.1,0.10, 0.0), black);
iso.add(Shape.Prism(Point(6.0,5,0.8), 0, 0.53, 0.3), black);
iso.add(Shape.Prism(Point(6.0,5.0,0.82), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(6.0,5.4,0.82), 0.0, 0.12, 0.1), yellow);
//rpi */
iso.add(Shape.Prism(Point(4.5, -1.5, 7), 3, 2.1, 0.8));
iso.add(Shape.Prism(Point(10.9,6.25,0.7), 0.1, 0.73, 0.5), gray);
iso.add(Shape.Prism(Point(10.9,5.7,1.0), 0.1, 0.4, 0.2), gray);
iso.add(Shape.Prism(Point(10.9,5.7,0.7), 0.1, 0.4, 0.2), gray);
iso.add(Shape.Prism(Point(10.9,5.1,0.7), 0.1, 0.4, 0.2), gray);
iso.add(Shape.Prism(Point(10.9,5.1,1.0), 0.1, 0.4, 0.2), gray);
iso.add(Shape.Prism(Point(10.9,6.4,0.8), 0, 0.53, 0.3), black);
iso.add(Shape.Prism(Point(10.9,6.4,0.82), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(10.9,6.75,0.82), 0.0, 0.12, 0.1), yellow);

/*iso.add(Shape.Prism(Point(3.75, 4.5, 1.36), 0.3, .36, .35), black);
iso.add(Shape.Prism(Point(3.1, 4.3, 1.5), 0.5, .5, .4), yellow);
iso.add(Shape.Prism(Point(-0.7, 5.0, 1.1), 4.3, .1, .1), yellow);
iso.add(Shape.Prism(Point(-0.7, -1.5, 1.1), 0.1, 6.5, .1), yellow);
*/


iso.add(Shape.Prism(Point(8, 7, 2.5), .4, .0, .1), white);
iso.add(Shape.Prism(Point(8, 7, 2.3), .4, .0, .1), white);
iso.add(Shape.Prism(Point(8, 7, 2.1), .4, .0, .1), white);


iso.add(Shape.Prism(Point(8.2, 7, 3.5), .1, .0, .1), white);
iso.add(Shape.Prism(Point(8.2, 7, 3.3), .1, .0, .1), white);
iso.add(Shape.Prism(Point(8.2, 7, 3.1), .1, .0, .1), white);

