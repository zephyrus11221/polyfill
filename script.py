import mdl
from display import *
from matrix import *
from draw import *
from sys import exit

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
frames = 0
basename = 'anim'
anim = False
knobs = {}

def first_pass( commands, symbols ):
    i = 0
    while (commands[i][0]!='frames' and i<len(commands)-1):
        i+=1
    if commands[i][0] == 'frames':
        print 'wassup'
        global frames
        frames = commands[i][1]
        for x in range(frames):
            knobs[x] = {}
        i = 0
        while (commands[i][0]!='basename' and i<len(commands)-1):
            i+=1
        if commands[i][0]=='basename':
            global basename
            basename = commands[i][1]
        else:
            print "No basename present, using default name (anim)."
        second_pass(commands, symbols, frames)
        return True
    elif 'vary' in symbols:
        print "Varying without frames. Invalid usage."
        exit()
    else:
        print "No animation commands, making single frame."
        return False
    pass


"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, symbols, num_frames ):
    verror = 'Invalid variance range.'
    print num_frames
    for i in commands:
        if i[0] == 'vary':
            print i[1]
            if i[2]>i[3]:
                print verror + ' Start is greater than end.'
                exit()
            if i[3]>=num_frames:
                print verror + ' End is greater than total frames.'
                print 'invalid: '+str(i[3])
                exit()
            if i[2]<0 or i[3]<0:
                print verror + ' Negative bounds.'
                exit()
            val = []
            symbols[i[1]][1] = i[4]
            if i[4]<i[5]:
                #print 'printing the bounds: ' + str(i[4])
                #print i[5]-i[4]
                #print 'printing the iteration: ' + str((i[5]-i[4])/(i[3]-i[2]))
                n = i[4]
                t = (float(i[5])-i[4])/(i[3]-i[2])
                iframe = i[2]
                while n<i[5]:
                    #print iframe
                    #print 'printing n: ' + str(n)
                    knobs[iframe][i[1]] = n
                    iframe += 1
                    n += t                

            else:
                print 'yallo'
                n = i[4]
                t = (float(i[5])-i[4])/(i[3]-i[2])
                iframe = i[2]
                while n>i[5]:
                    #print iframe
                    #print 'printing n: ' + str(n)
                    knobs[iframe][i[1]] = n
                    iframe += 1
                    n += t                
    print knobs
    pass


def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)
    print p
    print 'printed p'
    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    ident(tmp)
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.1

    anim = first_pass(commands, symbols)
    print 'printing anim: ' + str(anim)
    if(not anim):
        print 'oh'
        for command in commands:
            print command
            c = command[0]
            args = command[1:]

            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
    else:
        fn = 0
        fname = basename
        print fname
        while fn<frames:
            if (fn<10):
                fname = 'anim/' + basename + '00' + str(fn) + '.png'
            elif(fn<100):
                fname = 'anim/' + basename + '0' + str(fn) + '.png'
            else:
                fname = 'anim/' + basename + str(fn) + '.png'
            for knob in knobs[fn]:
                symbols[knob] = knobs[fn][knob]
            for command in commands:
                print command
                c = command[0]
                args = command[1:]

                if c == 'box':
                    if(type(args[-1]) is str):
                        for x in args[:-1]:
                            x *= symbols[args[-1]]
                    add_box(tmp,
                            args[0], args[1], args[2],
                            args[3], args[4], args[5])
                    matrix_mult( stack[-1], tmp )
                    draw_polygons(tmp, screen, color)
                    tmp = []
                elif c == 'sphere':
                    if(type(args[-1]) is str):
                        for x in args[:-1]:
                            x *= symbols[args[-1]]
                    add_sphere(tmp,
                               args[0], args[1], args[2], args[3], step)
                    matrix_mult( stack[-1], tmp )
                    draw_polygons(tmp, screen, color)
                    tmp = []
                elif c == 'torus':
                    if(type(args[-1]) is str):
                        for x in args[:-1]:
                            x *= symbols[args[-1]]
                    add_torus(tmp,
                              args[0], args[1], args[2], args[3], args[4], step)
                    matrix_mult( stack[-1], tmp )
                    draw_polygons(tmp, screen, color)
                    tmp = []
                elif c == 'move':
                    nargs = []
                    if(type(args[-1]) is str):
                        print 'yello'
                        print args[-1]
                        for x in range(len(args)-1):
                            print symbols[args[-1]]
                            print args[x]
                            nargs.append(args[x] * symbols[args[-1]])
                    else:
                        nargs = args
                    print 'printing args/nargs:'
                    print args
                    print nargs
                    tmp = make_translate(nargs[0], nargs[1], nargs[2])
                    matrix_mult(stack[-1], tmp)
                    stack[-1] = [x[:] for x in tmp]
                    tmp = []
                elif c == 'scale':
                    nargs = []
                    if(type(args[-1]) is str):
                        print 'yello'
                        print args[-1]
                        for x in range(len(args)-1):
                            print symbols[args[-1]]
                            print args[x]
                            nargs.append(args[x] * symbols[args[-1]])
                    else:
                        nargs = args
                    print 'printing args/nargs:'
                    print args
                    print nargs
                    tmp = make_scale(nargs[0], nargs[1], nargs[2])
                    print_matrix(tmp)
                    print_matrix(stack[-1])
                    matrix_mult(stack[-1], tmp)
                    stack[-1] = [x[:] for x in tmp]
                    print_matrix(stack[-1])
                    tmp = []
                elif c == 'rotate':
                    theta = args[1] * (math.pi/180)
                    if(type(args[-1]) is str):
                        theta *= symbols[args[-1]]
                    if args[0] == 'x':
                        tmp = make_rotX(theta)
                    elif args[0] == 'y':
                        tmp = make_rotY(theta)
                    else:
                        tmp = make_rotZ(theta)
                    matrix_mult( stack[-1], tmp )
                    stack[-1] = [ x[:] for x in tmp]
                    tmp = []
                elif c == 'push':
                    stack.append([x[:] for x in stack[-1]] )
                elif c == 'pop':
                    stack.pop()
            tmp = new_matrix()
            ident(tmp)
            stack = [ [x[:] for x in tmp] ]
            tmp = []
            print 'saving'
            save_extension(screen, fname)
            screen = new_screen()
            fn+= 1
