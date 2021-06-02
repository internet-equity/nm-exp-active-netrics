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
iso.add(Shape.Prism(Point(5.1, 6.2, 1.35), 0.4, .4, .35), black);
iso.add(Shape.Prism(Point(5.3, 6.1, 1.1), 0.5, .4, .4), yellow)
iso.add(Shape.Prism(Point(5.6, 4.1, 1.1), 0.1, 2.1, .1), yellow);
iso.add(Shape.Prism(Point(3.6, 4.1, 1.1), 2.0, .1, .1), yellow);
iso.add(Shape.Prism(Point(3.6, 1.8, 1.1), 0.1, 2.4, .1), yellow);
iso.add(Shape.Prism(Point(5.65, 1.8, 1.1), .1, .1, .8), yellow);
iso.add(Shape.Prism(Point(3.65, 1.8, 1.1), 2.0, .1, .1), yellow);


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

//internet outlet
iso.add(Shape.Prism(Point(10.35,9.5,2), 0,2, 3.55), lgray);
iso.add(Shape.Prism(Point(10.35,9.8,2.5), 0.02,1.5, 2.55), white);

iso.add(Shape.Prism(Point(10.35,9.9,3.6), 0.02,1.3, 0.1), lgray);

iso.add(Shape.Prism(Point(10.35,10.1,4.), 0.0,.8, 0.65), lgray);
iso.add(Shape.Prism(Point(10.35,10.3,4.3), 0.0,.05, 0.2), black);
iso.add(Shape.Prism(Point(10.35,10.6,4.3), 0.0,.05, 0.2), black);
iso.add(Shape.Prism(Point(10.35,10.45,4.1), 0.0,.05, 0.1), black);

//iso.add(Shape.Prism(Point(13.35,6.7,0.7), 0.1,.8, .65), lgray);
//iso.add(Shape.Prism(Point(13.35,6.9,0.9), 0.0,0.45, 0.3), black);

//usb charger
iso.add(Shape.Prism(Point(8.95,12.25,2.3),0.32,0.05, 0.2), lgray);
iso.add(Shape.Prism(Point(8.95,12.50,2.3),0.32,0.05, 0.2), lgray);
iso.add(Shape.Prism(Point(9.0,12.5,1.9), 0.2,0.5, .55), llgray);

iso.add(Shape.Prism(Point(9.0,13.3,.45), 0.8,0.6, 1.3), llgray);
iso.add(Shape.Prism(Point(9.0,13.55,1.5), 0.0, 0.1, 0.1), red);


//mini usb
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

//modem
iso.add(Shape.Prism(Point(2, -5.35, 7.0), 4, 1.6, 3.5), llgray);
iso.add(Shape.Prism(Point(8.1,1.3,2.8), 0.1, 0.73, 0.5), llgray);
iso.add(Shape.Prism(Point(8.1,1.4,2.89), 0.0, 0.53, 0.3), black);
iso.add(Shape.Prism(Point(8.1,1.8,2.82), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(8.1,1.4,2.82), 0.0, 0.12, 0.1), yellow);
iso.add(Shape.Prism(Point(8.1,1.3,1.8), 0.1, 0.73, 0.5), llgray);
iso.add(Shape.Prism(Point(8.1,1.4,1.89), 0.0, 0.53, 0.3), black);
iso.add(Shape.Prism(Point(8.1,1.8,1.82), 0.0, 0.12, 0.1), green);
iso.add(Shape.Prism(Point(8.1,1.4,1.82), 0.0, 0.12, 0.1), yellow);


//eth internet
iso.add(Shape.Prism(Point(6.75, 1.0, 2.36), 0.3, .36, .35), black);
iso.add(Shape.Prism(Point(6.1, 0.8, 2.5), 0.5, .5, .4), yellow);
iso.add(Shape.Prism(Point(5.4, 1.5,2.1), 1.15, .1, .1), yellow);


