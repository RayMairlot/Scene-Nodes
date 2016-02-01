import bpy
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

bpy.types.Scene.graphing = bpy.props.BoolProperty(default=False)

class GraphScene(bpy.types.Operator):
    """Add a simple box mesh"""
    bl_idname = "scene_nodes.graph_scene"
    bl_label = "Add Box"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        
        #Stops scenes from being deleted when nodes are cleared
        context.scene.graphing = True
        
        bpy.data.node_groups['NodeTree'].nodes.clear()           

        for sceneIndex, scene in enumerate(bpy.data.scenes):
            
            newSceneNode = bpy.data.node_groups['NodeTree'].nodes.new('SceneNodeType')
            newSceneNode.sceneIndex = sceneIndex
            newSceneNode.select = False
            newSceneNode.location[1] = sceneIndex * -newSceneNode.height
            
            for objectIndex, object in enumerate(scene.objects):
                
                newObjectNode = bpy.data.node_groups['NodeTree'].nodes.new('ObjectNodeType')
                newObjectNode.objectIndex = objectIndex
                newObjectNode.select = False
                newObjectNode.location[1] = objectIndex * (-newObjectNode.height - 20)
                newObjectNode.location[0] = newSceneNode.width + 30
                
                
                #node = bpy.context.scene.node_tree.nodes 
                bpy.data.node_groups['NodeTree'].links.new(newObjectNode.inputs[0], newSceneNode.outputs[0])  
            
        context.scene.graphing = False
            
        return {'FINISHED'}



# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class SceneTree(NodeTree):
    '''Scene Nodes'''
    bl_idname = 'SceneTreeType'
    bl_label = 'Scene'
    bl_icon = 'SCENE_DATA'


# Custom socket type
class MyCustomSocket(NodeSocket):
    '''Custom node socket type'''
    bl_idname = 'CustomSocketType'
    bl_label = 'Custom Node Socket'

    my_items = [
        ("DOWN", "Down", "Where your feet are"),
        ("UP", "Up", "Where your head should be"),
        ("LEFT", "Left", "Not right"),
        ("RIGHT", "Right", "Not left")
    ]

    myEnumProperty = bpy.props.EnumProperty(name="Direction", description="Just an example", items=my_items, default='UP')

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "myEnumProperty", text=text)

    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)


# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class MyCustomTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SceneTreeType'


# Derived from the Node base type.
class SceneNode(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'SceneNodeType'
    bl_label = 'Scene'
    bl_icon = 'SCENE_DATA'

    sceneIndex = bpy.props.IntProperty()
    
    #newScene = bpy.props.BoolProperty(default=False)
#    otherIndex = len(bpy.data.scenes)

#    print(sceneIndex)
##        
#    if newScene:
#        
#        bpy.data.scenes.new("Scene")
#        
#        sceneIndex = len(bpy.data.scenes)-1


    # === Optional Functions ===
    # Initialization function, called when a new node is created.
    # This is the most common place to create the sockets for a node, as shown below.
    # NOTE: this is not the same as the standard __init__ function in Python, which is
    #       a purely internal Python method and unknown to the node system!
    def init(self, context):
        #self.inputs.new('CustomSocketType', "Hello")
        self.outputs.new('NodeSocketFloat', "Scene")
        

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)
        
        bpy.data.scenes.new("Scene")
        self.sceneIndex = self.sceneIndex + 1

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        
        #Don't delete scene if node is deleted during graphing and scene isn't last scene
        if len(bpy.data.scenes) > 0 and not bpy.context.scene.graphing:
            
            bpy.data.scenes.remove(bpy.data.scenes[self.sceneIndex])

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):

        layout.prop(bpy.data.scenes[self.sceneIndex], "name", text="", icon="SCENE_DATA")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
#    def draw_buttons_ext(self, context, layout):
#        layout.prop(self, "myFloatProperty")
#        # myStringProperty button will only be visible in the sidebar
#        layout.prop(self, "myStringProperty")

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Scene Node"



class ObjectNode(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'ObjectNodeType'
    bl_label = 'Object'
    bl_icon = 'OBJECT_DATA'

    objectIndex = bpy.props.IntProperty()


    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Parent")
        self.outputs.new('NodeSocketFloat', "Child")
        

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)
        
    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):

        layout.prop(bpy.data.objects[self.objectIndex], "name", text="", icon="OBJECT_DATA")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
#    def draw_buttons_ext(self, context, layout):
#        layout.prop(self, "myFloatProperty")
#        # myStringProperty button will only be visible in the sidebar
#        layout.prop(self, "myStringProperty")

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Object Node"



### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SceneTreeType'

# all categories in a list
node_categories = [
    # identifier, label, items list
    MyNodeCategory("SOMENODES", "Some Nodes", items=[
        # our basic node
        NodeItem("SceneNodeType"),
        NodeItem("ObjectNodeType"),
        ]),
    MyNodeCategory("OTHERNODES", "Other Nodes", items=[
        # the node item can have additional settings,
        # which are applied to new nodes
        # NB: settings values are stored as string expressions,
        # for this reason they should be converted to strings using repr()
        NodeItem("SceneNodeType", label="Node A", settings={
            "newScene": repr(True)
            })
        ]),
    ]



def SceneNodesHeader(self, context):
    
    layout = self.layout
    
    row = layout.row()
    row.operator("scene_nodes.graph_scene", text="Graph Scene")



def register():
    bpy.utils.register_class(SceneTree)
    bpy.utils.register_class(MyCustomSocket)
    bpy.utils.register_class(SceneNode)
    bpy.utils.register_class(ObjectNode)    
    bpy.utils.register_class(GraphScene)

    bpy.types.NODE_HT_header.append(SceneNodesHeader)

    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)
    


def unregister():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")

    bpy.utils.unregister_class(MyCustomTree)
    bpy.utils.unregister_class(MyCustomSocket)
    bpy.utils.unregister_class(SceneNode)
    bpy.utils.register_class(ObjectNode)
    bpy.utils.unregister_class(GraphScene)

#if __name__ == "__main__":
#    register()
#    

register()    
