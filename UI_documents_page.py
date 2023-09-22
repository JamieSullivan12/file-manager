import tkinter as tk
import customtkinter as ctk
import UI_Popup_Edit_Row

class DocumentViewerPage(ctk.CTkScrollableFrame):

    class DocumentViewerTab():
        def __init__(self,parent,mainline_obj,paper_obj,name,new_document=False):
            self.parent=parent
            self.mainline_obj=mainline_obj
            self.paper_obj=paper_obj
            self.name = name
            self.id = paper_obj.get_id()
            self.new_document=new_document
            self.loadnew_window = None

            self.setup_tab()




        def setup_tab(self):

            if self.name == "New":
                self.type="create"
            else: 
                self.type="update"
            
                if self.paper_obj.get_name()=="": self.name = "Empty"
                else: 
                    self.name = self.paper_obj.get_name()
            suffix = ""

            i = 1
            while self.parent.check_exists(self.name + suffix) == True:
                suffix = f" ({i})"
                i += 1
            self.name = self.name + suffix
                

            self.parent.tabview.insert(0,self.name)
            self.loadwindow()

            if self.parent.tabview.get() != self.name:
                self.parent.tabview.set(self.name)

        def change_name(self,new_name):
            self.name = new_name
            self.setup_tab()

        def closewindow(self):
            self.parent.remove_tab(self)

        def loadwindow(self):


            self.parent.tabview.tab(self.name).columnconfigure(0,weight=1)

            if self.loadnew_window == None:
                self.loadnew_window = UI_Popup_Edit_Row.UIPopupEditRow(self.mainline_obj, self.parent.tabview.tab(self.name),paper_obj=self.paper_obj,type=self.type,tab_link=self.id,new_document=self.new_document)
            else:
                self.loadnew_window.grid_forget()
                self.loadnew_window.configure(master = self.parent.tabview.tab(self.name))
                self.loadnew_window.grid(row=1,column=0,sticky="nsew")


    def add_to_pack(self,expand=False,anchor="n",fill="both"):
        self.pack(expand=expand, anchor=anchor, fill=fill)

    def remove_from_pack(self):
        self.pack_forget()

    def check_exists(self,tab_name):
        exists = False
        for tab in self.tabs_dict:
            if self.tabs_dict[tab].name == tab_name:
                exists=True
        return exists

    def remove_tab(self,tab_object):
        self.tabview.delete(tab_object.name)
        del self.tabs_dict[tab_object.id]


    def change_tab_name(self,tab_code,new_name):
        self.tabs_dict[tab_code].change_name(new_name)

    def reset_tab(self,old_name,paper_obj):
        self.remove_tab(self.tabs_dict[old_name])
        new_tab = self.DocumentViewerTab(self,self.mainline_obj,paper_obj,paper_obj.get_name())
        self.tabs_dict[paper_obj.get_id()]=new_tab
        self.mainline_obj.top_frame_resize_event(specific="DocumentViewerPage")

    def create_new_document(self):

        new_document_object = self.mainline_obj.db_object.create_new_row()

        new_tab = self.DocumentViewerTab(self,self.mainline_obj,new_document_object,"New",new_document=True)        
        self.tabs_dict[new_document_object.get_id()]= new_tab
        self.tabviewconfigure()
        self.mainline_obj.top_frame_resize_event(specific="DocumentViewerPage")



    def open_existing_document(self,paper_obj):
        if paper_obj.get_id() in self.tabs_dict:
            self.tabview.set(self.tabs_dict[paper_obj.get_id()].name)
        else:
            
            new_tab = self.DocumentViewerTab(self,self.mainline_obj,paper_obj,paper_obj.get_name())        
            self.tabs_dict[paper_obj.get_id()] = new_tab
            self.tabviewconfigure()
            self.mainline_obj.top_frame_resize_event(specific="DocumentViewerPage")


    def closeopentab(self):
        open_tab = self.tabview.get()
        for tab in self.tabs_dict:
            if self.tabs_dict[tab].name == open_tab:
                self.tabs_dict[tab].closewindow()
                break
        self.tabviewconfigure()

    def tabviewconfigure(self):
        if self.tabview.get()=="":
            self.tabview.configure(border_width=0)
        else:
            self.tabview.configure(border_width=2)
        pass
    def make_grid(self,critical=False):
        for tab_id in self.tabs_dict:
            self.tabs_dict[tab_id].loadnew_window.make_grid(critical=critical)
    def __init__(self,mainline_obj, scrollable_frame, grid_preload=  False):
        super().__init__(scrollable_frame)
        self.columnconfigure(0,weight=1)

        self.bubble_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=mainline_obj.colors.bubble_background)
        self.bubble_frame.grid(row=0,column=0,padx=15,pady=15,sticky="nsew")


        self.tabview = ctk.CTkTabview(master=self.bubble_frame,fg_color=self.cget("fg_color"),border_color="black")
        self.tabview.grid(row=1,column=0,columnspan=2,sticky="nsew",padx=15,pady=(7,15))
        self.tabview.columnconfigure(0,weight=1)
        

        self.bubble_frame.columnconfigure(0,weight=1)
        self.bubble_frame.columnconfigure(1,weight=1)


        self.mainline_obj=mainline_obj
        self.tabs_dict={}
        #.tabview.configure(width = 1000)
        self.createnewbutton = ctk.CTkButton(self.bubble_frame,text="New document",command=self.create_new_document)
        self.createnewbutton.grid(row=0,column=0,sticky="new",padx=(15,7),pady=(15,7))
        
        
        self.close_window = ctk.CTkButton(self.bubble_frame,text="Close open tab",command=self.closeopentab)
        self.close_window.grid(row=0,column=1,sticky="new",padx=(7,15),pady=(15,7))
