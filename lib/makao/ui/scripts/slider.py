import java

import javax.swing
from javax.swing import JDialog

from javax.swing import JRadioButton
from javax.swing import ButtonGroup

from com.hp.hpl.guess.ui import DockableAdapter

#import com

#from java.text import SimpleDateFormat

#from org.joda.time import DateTime
#from org.joda.time import Days
#from org.joda.time import Duration
#from org.joda.time import Interval
#from org.joda.time import MutableDateTime
#from org.joda.time import Period
#from org.joda.time.format import DateTimeFormatter
#from org.joda.time.format import DateTimeFormatterBuilder

#import java.util
#from java.util.concurrent import LinkedBlockingQueue
#from java.util.concurrent import ThreadPoolExecutor
#from java.util.concurrent import TimeUnit

import time

class slider(DockableAdapter):

    def __init__(self):
        self.min=min(g.edges.tstamp)-1
        self.max=max(g.edges.tstamp)

        self.testSlider = JSlider()  # keep the label and slider

        self.replayer=replay()

        max_node=node_at_tstamp(self.max)
        self.label = JLabel(pad_string(max_node.name+": "+max_node.localname,100,110))
        self.label.setOpaque(true)
        self.label.setBackground(Color.white)

        # set up the slider limits
        self.testSlider.setMinimum(self.min)
        self.testSlider.setMaximum(self.max)

        # set up the slider visual properties
#         self.testSlider.setMajorTickSpacing(50)
#         self.testSlider.setMinorTickSpacing(10)
#         self.testSlider.setMajorTickSpacing(60*60*24)
#         self.testSlider.setPaintTicks(true)
#         self.testSlider.setPaintLabels(true)
#         self.testSlider.setValue(self.days)  # default value
        self.testSlider.setValue(self.max)  # default value

        # every time the mouse is released call the "sc" method
        self.testSlider.mouseReleased = self.sc

#        self.oneButton = JButton("Jump to Dep. Graph Constr.")
#         self.oneButton.setForeground(Color.GREEN)
#        self.oneButton.actionPerformed = self.one

#        self.twoButton = JButton("Jump to Actual Constr.")
#         self.nextButton.setForeground(Color.GREEN)
#        self.twoButton.actionPerformed = self.two
         
        self.prevButton = JButton("Previous")
#        self.prevButton.setForeground(Color.GREEN)
        self.prevButton.actionPerformed = self.previous

        self.nextButton = JButton("Next")
#        self.nextButton.setForeground(Color.GREEN)
        self.nextButton.actionPerformed = self.next

        self.centerButton = JButton("CENTER")
        self.centerButton.setForeground(Color.RED)
        self.centerButton.actionPerformed = lambda event: v.center()
        
        self.animButton = JButton("Play Back")
        self.animButton.actionPerformed = self.animate

        # add the toggler, label and slider to the UI
        layout=GroupLayout(self)
        self.setLayout(layout)
        layout.setAutoCreateGaps(true);
        layout.setAutoCreateContainerGaps(true);
        layout.setHorizontalGroup(
            layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.CENTER)
                      .addComponent(self.centerButton)
                      .addComponent(self.animButton))
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.CENTER)
                      .addComponent(self.testSlider)
                      .addComponent(self.label))
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.CENTER)
                      .addComponent(self.prevButton)
#                      .addComponent(self.animButton))
#            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.CENTER)
                      .addComponent(self.nextButton))
            )

        layout.setVerticalGroup(
            layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.CENTER)
                      .addComponent(self.centerButton)
                      .addComponent(self.testSlider)
                      .addComponent(self.prevButton))
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.CENTER)                      
                      .addComponent(self.animButton)
                      .addComponent(self.label)
#                      .addComponent(self.animButton)
                      .addComponent(self.nextButton))
            )

        # dock the new panel into the UI
        ui.dock(self)

    def getTitle(self):
        return("Time Slider")

    def reset(self):
        self.replayer.reset_to_max()

    def sc(self,evt):

        # get the value
        selected_epoch = self.testSlider.getValue()
        if selected_epoch>self.replayer.current_tstamp:
            selected_epoch=self.replayer.next_existing_tstamp(selected_epoch)
            self.replayer.goto(selected_epoch,1)
        elif selected_epoch<self.replayer.current_tstamp:
            selected_epoch=self.replayer.prev_existing_tstamp(selected_epoch)
            self.replayer.goback(selected_epoch,1)

        return true

    def previous(self,evt):

        # get the value
#        val = long(self.testSlider.getValue())
#        if val==self.testSlider.getMinimum():
#           return false
        self.replayer.prev(1,1)
        return true

    def next(self,evt):

        # get the value
#        val = long(self.testSlider.getValue())
#        if val==self.testSlider.getMaximum():
#           return false

        self.replayer.next(1,1)
        return true

    def animate(self,evt):

        options = ["Yes, please","No, thanks"]
        scrollPane=JScrollPane()
        scrollPane.setPreferredSize(Dimension(200,75))
        textArea = JTextArea("Animation can take a long time and *cannot* yet be interrupted, are you sure you want to proceed?");  
        textArea.setLineWrap(true);  
        textArea.setWrapStyleWord(true);  
        textArea.setMargin(Insets(5,5,5,5));  
        scrollPane.getViewport().setView(textArea);
        textArea.setCaretPosition(0)
        choice = JOptionPane.showOptionDialog(self,scrollPane, "Look out!",JOptionPane.YES_NO_OPTION,JOptionPane.WARNING_MESSAGE,None,options,options[0])
        if choice==1:
           return

#        self.replayer.goback(-1)
        self.replayer.reset_to_min()
       
#        print self.replayer.current_tstamp

        while self.replayer.current_tstamp<self.max:
            i=self.replayer.next_existing_tstamp(self.replayer.current_tstamp)
#            print "in "+str(i)+" right now"
            self.replayer.next(1,0)
            edd=self.replayer.edge_dictionary[self.replayer.current_tstamp]

            skip_drawing=false
            next_up=self.replayer.next_existing_tstamp(self.replayer.current_tstamp)
            if next_up <= self.max:
                next_edd=self.replayer.edge_dictionary[next_up]
                if edd.node1 == next_edd.node1:
                    skip_drawing=true

            if not skip_drawing:
                v.repaint()
                v.paintImmediately()            
                time.sleep(0.01)

#        print "Finished!"

    def update_label(self,msg):
        self.label.setText(pad_string(msg,100,110))

