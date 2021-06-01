var Point  = Isomer.Point;
var Path   = Isomer.Path;
var Shape  = Isomer.Shape;
var Vector = Isomer.Vector;
var Color  = Isomer.Color;

var iso = new Isomer(document.getElementById("canvas"));

var red = new Color(160, 60, 50);
var blue = new Color(80, 90, 160);
var bluey = new Color(20, 70, 90);
var gray = new Color(40, 40, 40);
var green = new Color(0, 255, 0);
var yellow = new Color(255, 190, 0);
var black = new Color(0, 0, 0);
var lgray = new Color(180, 180, 180);
var llgray = new Color(80, 80, 80);
var white = new Color(250, 250, 250);
var blue = new Color(0, 150, 255);


//eth cable
iso.add(Shape.Prism(Point(7.6, 3.0, 1.1), 0.1, 1.2, .1), yellow);
iso.add(Shape.Prism(Point(5.1, 6.2, 1.35), 0.4, .4, .35), black);
iso.add(Shape.Prism(Point(5.3, 6.1, 1.1), 0.5, .4, .4), yellow)
iso.add(Shape.Prism(Point(5.6, 4.1, 1.1), 0.1, 2.1, .1), yellow);
iso.add(Shape.Prism(Point(5.6, 4.1, 1.1), 2.0, .1, .1), yellow);
iso.add(Shape.Prism(Point(3.6, 3.0, 1.1), 4.0, .1, .1), yellow);
iso.add(Shape.Prism(Point(3.6, 1.8, 1.1), 0.1, 1.2, .1), yellow);
iso.add(Shape.Prism(Point(7.6, 0.7, 1.1), 0.1, 1.2, .1), yellow);
iso.add(Shape.Prism(Point(3.6, 1.8, 1.1), 4.0, .1, .1), yellow);


iso.add(Shape.Prism(Point(5.0, 0.7, 1.1), 2.6, .1, .1), yellow);

iso.add(Shape.Prism(Point(4.3, 0.4, 1.1), 0.5, .5, .4), yellow);
iso.add(Shape.Prism(Point(3.75, 0.22, 1.36), 0.3, .36, .35), black);


//rpi
iso.add(Shape.Prism(Point(-2, 1.5, 7.0), 2, 3, 0.8), gray);
iso.add(Shape.Prism(Point(5.5,7.8,0.8), 0.73, 0.1, 0.5), gray);
iso.add(Shape.Prism(Point(5.0,7.8,1.1), 0.4, 0.1, 0.2), gray);
iso.add(Shape.Prism(Point(5.0,7.8,0.8), 0.4, 0.1, 0.2), gray);
iso.add(Shape.Prism(Point(5.0,7.8,1.2), 0.4, 0.0, 0.05), blue);
iso.add(Shape.Prism(Point(5.0,7.8,0.9), 0.4, 0.0, 0.05), blue);

iso.add(Shape.Prism(Point(4.5,7.8,0.8), 0.4, 0.1, 0.2), gray);
iso.add(Shape.Prism(Point(4.5,7.8,1.1), 0.4, 0.1, 0.2), gray);
iso.add(Shape.Prism(Point(4.5,7.8,1.2), 0.4, 0.0, 0.05), black);
iso.add(Shape.Prism(Point(4.5,7.8,0.9), 0.4, 0.0, 0.05), black);

iso.add(Shape.Prism(Point(5.6,7.8,0.82), 0.12, 0.0, 0.1), green);
iso.add(Shape.Prism(Point(6.0,7.8,0.82), 0.12, 0.0, 0.1), yellow);
iso.add(Shape.Prism(Point(5.6,7.8,0.95), 0.53, 0, 0.3), black);
iso.add(Shape.Prism(Point(3.9,8.8,1.2), 0.1, 0.4, 0.2), gray);
iso.add(Shape.Prism(Point(3.9,9.9,1.2), 0.1, 0.3, 0.1), gray);


/*
//power outlet
iso.add(Shape.Prism(Point(13.10,10.7,-0.3), 0,2, 3.55), lgray);
iso.add(Shape.Prism(Point(13.10,11.0,0.2), 0.02,1.5, 2.55), white);
iso.add(Shape.Prism(Point(13.10,11.1,1.3), 0.02,1.3, 0.1), lgray);
iso.add(Shape.Prism(Point(13.10,11.3,1.8), 0.0,.8, 0.65), lgray);
iso.add(Shape.Prism(Point(13.10,11.5,2.1), 0.0,.05, 0.2), black);
iso.add(Shape.Prism(Point(13.10,11.8,2.1), 0.0,.05, 0.2), black);
iso.add(Shape.Prism(Point(13.10,11.65,1.9), 0.0,.05, 0.1), black);
*/

//iso.add(Shape.Prism(Point(13.35,10.7,0.7), 0.1,.8, .65), lgray);
//iso.add(Shape.Prism(Point(13.35,10.9,0.9), 0.0,0.45, 0.3), black);

//usb charger
iso.add(Shape.Prism(Point(8.95,12.25,2.3), 0.32,0.05, 0.2), lgray);
iso.add(Shape.Prism(Point(8.95,12.50,2.3), 0.32,0.05, 0.2), lgray);
iso.add(Shape.Prism(Point(9.0,12.5,1.9), 0.2,0.5, .55), llgray);

iso.add(Shape.Prism(Point(9.0,13.3,.45), 0.8,0.6, 1.3), llgray);
//iso.add(Shape.Prism(Point(10.0,12.2,0.7), 0.1, 0.2, 0.4), gray);
iso.add(Shape.Prism(Point(9.0,13.55,1.5), 0.0, 0.1, 0.1), red);
//iso.add(Shape.Prism(Point(9.2,12.0,1.0), 0.3,0.25, 0.45), llgray);


//mini usb
//iso.add(Shape.Prism(Point(8.5,12.05,1.0), 0.3,0.10, 0.45), lgray);
//iso.add(Shape.Prism(Point(8.63,12.05,1.05), 0.05,0.00, 0.10), black);
//iso.add(Shape.Prism(Point(8.63,12.05,1.2), 0.05,0.00, 0.10), black);

iso.add(Shape.Prism(Point(2.8,9.9,1.2), 0.2, 0.28, 0.05), lgray);
iso.add(Shape.Prism(Point(2.6,9.9,1.16), 0.2, 0.32, 0.1), llgray);
iso.add(Shape.Prism(Point(1.2,9.95,1.16), 1.36, 0.2, 0.08), llgray);
iso.add(Shape.Prism(Point(1.2,13.05,1.16), 7.3, 0.2, 0.08), llgray);
iso.add(Shape.Prism(Point(1.2,12.75,1.16), 0.2,0.4, 0.08), llgray);

iso.add(Shape.Prism(Point(1.1,10.95,1.16), 0.38,1.0, 0.18), llgray);
iso.add(Shape.Prism(Point(1.2,9.95,1.16), 0.2,1.0, 0.08), llgray);
iso.add(Shape.Prism(Point(1.15,12.6,1.16), 0.32, 0.2, 0.1), llgray);
iso.add(Shape.Prism(Point(1.2,12.4,1.15), 0.28, 0.2, 0.05), lgray);

iso.add(Shape.Cylinder(Point(2.3,12.2,0.36), 0.05,20,0), red);
iso.add(Shape.Cylinder(Point(2.3,12.5,0.36), 0.08,20,0.05), llgray);



//internet outlet
//iso.add(Shape.Prism(Point(13.35,6,0), 0,2, 3.55), lgray);
//iso.add(Shape.Prism(Point(13.35,6.3,0.5), 0.02,1.5, 2.55), white);

//iso.add(Shape.Prism(Point(13.35,6.4,1.6), 0.02,1.3, 0.1), lgray);

//iso.add(Shape.Prism(Point(13.35,6.6,2.), 0.0,.8, 0.65), lgray);
//iso.add(Shape.Prism(Point(13.35,6.8,2.3), 0.0,.05, 0.2), black);
//iso.add(Shape.Prism(Point(13.35,7.1,2.3), 0.0,.05, 0.2), black);
//iso.add(Shape.Prism(Point(13.35,6.95,2.1), 0.0,.05, 0.1), black);

//iso.add(Shape.Prism(Point(13.35,6.7,0.7), 0.1,.8, .65), lgray);
//iso.add(Shape.Prism(Point(13.35,6.9,0.9), 0.0,0.45, 0.3), black);

/*
//eth internet
iso.add(Shape.Prism(Point(10.75, 6.0, 1.36), 0.3, .36, .35), black);
iso.add(Shape.Prism(Point(10.1, 5.8, 1.5), 0.5, .5, .4), yellow);
iso.add(Shape.Prism(Point(9.6, 6.5, 1.1), 1.0, .1, .1), yellow);
iso.add(Shape.Prism(Point(9.6, -2.6, 1.1), 0.1, 9.2, .1), yellow);
iso.add(Shape.Prism(Point(8.0, -2.6, 1.1), 1.6, .1, .1), yellow);
iso.add(Shape.Prism(Point(7.3, -2.8, 1.1), 0.5, .5, .4), yellow);
iso.add(Shape.Prism(Point(6.75, -3.0, 1.36), 0.3, .36, .35), black);
*/

//router
//iso.add(Shape.Prism(Point(4, -5, 1), 1.5, 7, 1));
////iso.add(Shape.Prism(Point(5, 0.8, 2), 0.1, 0.1, 4));
////iso.add(Shape.Prism(Point(5, -4, 2), 0.1, 0.1, 4));
//iso.add(Shape.Prism(Point(1, -6.5, 3), 1, 6, 0.8));
//iso.add(Shape.Prism(Point(2, -5, 1), 1.5, 7, 1));
//iso.add(Shape.Prism(Point(1, -4.5, 1), 1, 6, 0.8));
//iso.add(Shape.Prism(Point(0.5,-5,1), 1.0, 7, 1));
//iso.add(Shape.Prism(Point(0.5,-1,1.2), 0.1, 0.5, 0.2), bluey);
//iso.add(Shape.Prism(Point(0.5,0.,1.2), 0.1, 0.5, 0.2), bluey);
//iso.add(Shape.Prism(Point(0.5,1,1.2), .1, 0.5, 0.2), bluey);
