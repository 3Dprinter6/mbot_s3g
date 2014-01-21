
import makerbot_driver, serial,threading

port="/dev/ttyACM0"
r = makerbot_driver.s3g()
file = serial.Serial(port, 115200, timeout=1)
r.writer = makerbot_driver.Writer.StreamWriter(file,threading.Condition())



#r.find_axes_maximums(['x', 'y'], 500, 60)
#r.find_axes_minimums(['z'], 500, 60)
#r.recall_home_positions(['x', 'y', 'z', 'a', 'b'])


r.queue_extended_point([-2000,0,2000,0,0], 400,0,0)
#r.queue_extended_point([2000,2000,2000,0,0], 400,0,0)
#r.queue_extended_point([0,2000,2000,0,0], 400,0,0)
#r.queue_extended_point([0,0,2000,0,0], 400,0,0)



#r.set_toolhead_temperature(0, 220)
#r.wait_for_tool_ready(0,100,5*60)
#r.queue_extended_point([0,0,5000,-5000,0], 2500,0,0)


#r.set_toolhead_temperature(0,0)
r.toggle_axes(['x','y','z','a','b'],False)
