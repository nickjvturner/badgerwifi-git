from PIL import Image, ImageDraw
import math

# Define start position and angle
start_pos = (50, 50)
angle = 30

# Create new image
img = Image.new('RGB', (200, 200), color = (255, 255, 255))

# Create draw object
draw = ImageDraw.Draw(img)

# Calculate end position based on angle and length of arrow
length = 50
end_pos = (start_pos[0] + int(length*math.cos(math.radians(angle))),
           start_pos[1] + int(length*math.sin(math.radians(angle))))

# Draw line
draw.line([start_pos, end_pos], fill='black', width=2)

# Draw arrowhead
arrow_size = 10
theta = math.atan2(end_pos[1]-start_pos[1], end_pos[0]-start_pos[0])
draw.polygon([(end_pos[0]+arrow_size*math.cos(theta-math.pi/6),
               end_pos[1]+arrow_size*math.sin(theta-math.pi/6)),
              (end_pos[0]+arrow_size*math.cos(theta+math.pi/6),
               end_pos[1]+arrow_size*math.sin(theta+math.pi/6)),
              end_pos], fill='black')

# Show image
img.show()
