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
        
        nodeGroup = bpy.data.node_groups['NodeTree']
        
        nodeGroup.nodes.clear()           


        for sceneIndex, scene in enumerate(bpy.data.scenes):
            
            newSceneNode = nodeGroup.nodes.new('SceneNodeType')
            newSceneNode.sceneIndex = sceneIndex
            newSceneNode.select = False
            newSceneNode.location[1] = sceneIndex * -newSceneNode.height
            
            #Only get objects that aren't children themselves
            totalHeight = len([object for object in scene.objects if object.parent == None]) * -110
            
            yOffset = 0
                          
            for objectIndex, object in enumerate(scene.objects):
                
                newObjectNode = nodeGroup.nodes.new('ObjectNodeType')
                newObjectNode.objectIndex = objectIndex
                newObjectNode.select = False
                newObjectNode.name = bpy.data.objects[objectIndex].name

                objectType = bpy.data.objects[objectIndex].type

                newObjectNode.use_custom_color = True
                
                if objectType == "MESH":
                    
                    newObjectNode.color = [1.000000, 0.792470, 0.552983]
                    
                elif objectType == "LAMP":
                    
                    newObjectNode.color = [1.000000, 0.936002, 0.395156]
                
                                
                if bpy.data.objects[objectIndex].parent == None:
                    
                    newObjectNode.location[1] = (yOffset * -140) - (totalHeight/2) + 12
                    newObjectNode.location[0] = newSceneNode.width + 80
                    
                    nodeGroup.links.new(newObjectNode.inputs[0], newSceneNode.outputs[0])  
                    
                    yOffset = yOffset + 1
                    
                else:
                    
                    parentName = bpy.data.objects[objectIndex].parent.name
                    
                    if len(nodeGroup.nodes[parentName].outputs['Child'].links) == 0:
                        
                        newObjectNode.location[1] = nodeGroup.nodes[parentName].location[1]
                        
                    else:
                        
                        totalChildren = len(nodeGroup.nodes[parentName].outputs['Child'].links)
                        
                        lastChild = nodeGroup.nodes[parentName].outputs['Child'].links[totalChildren-1].to_node
                        
                        newObjectNode.location[1] = lastChild.location[1] - 140
                        
                    
                    newObjectNode.location[0] = nodeGroup.nodes[parentName].location[0] + newObjectNode.width + 80
                    
                    nodeGroup.links.new(newObjectNode.inputs[0], nodeGroup.nodes[parentName].outputs[0])
                    
                
                for materialSlot in object.material_slots:
                    
                    objectMaterial = materialSlot.material
                    
                    newMaterialNode = nodeGroup.nodes.new('MaterialNodeType')
                    
                    for materialIndex, material in enumerate(bpy.data.materials):
                        
                        if objectMaterial.name == material.name:
                            
                            newMaterialNode.materialIndex = materialIndex
                            
                            break
                    
                    newMaterialNode.select = False
                    newMaterialNode.location[1] = newObjectNode.location[1]
                    newMaterialNode.location[0] = newObjectNode.location[0] + newObjectNode.width + 80
                    newMaterialNode.name = bpy.data.materials[materialIndex].name
                    newMaterialNode.use_custom_color = True                   
                    newMaterialNode.color = [1.000000, 0.608448, 0.993887]
                    
                    nodeGroup.links.new(newMaterialNode.inputs[0], newObjectNode.outputs[1])
                                                                                   
                    
            
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
        self.outputs.new('NodeSocketFloat', "Material")
        

    def update(self):
        
        #print("updating node: ", self.name, len(self.inputs[0].links))
        
        if len(self.inputs[0].links) != 1:
            
            bpy.data.objects[self.objectIndex].parent = None
            
            sceneName = bpy.data.objects[self.objectIndex].users_scene[0].name
            
            nodeGroup = bpy.data.node_groups['NodeTree']
            
            nodeGroup.links.new(self.inputs[0], nodeGroup.nodes[sceneName].outputs[0])  
            
        else:
            
            parentName = self.inputs[0].links[0].from_node.name
                                    
            #print(parentName)
            
            if parentName != "Scene":
            
                bpy.data.objects[self.objectIndex].parent = bpy.data.objects[parentName]
        

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)
        
        object = bpy.data.objects[self.objectIndex]
        
        scene = bpy.data.objects[self.objectIndex].users_scene[0]
                
        if object.type == "CAMERA":
            
            newCamera = bpy.data.cameras.new(object.name)
            
            newObject = bpy.data.objects.new(object.name, newCamera)
            
            scene.objects.link(newObject)
            scene.update()
            
            #bpy.ops.scene_nodes.graph_scene()
            
            ################################################
            #Need to re-index after duplicating.
            #Compare list of objects before duplicating and after to see difference.
            
            
            
        
    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):

        layout.prop(bpy.data.objects[self.objectIndex], "name", text="", icon=bpy.data.objects[self.objectIndex].type+"_DATA")

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



class MaterialNode(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'MaterialNodeType'
    bl_label = 'Material'
    bl_icon = 'MATERIAL_DATA'

    materialIndex = bpy.props.IntProperty()


    def init(self, context):
                
        self.inputs.new('NodeSocketFloat', "Object")
        
        
    def update(self):
        
        print("updating node: ", self.name, len(self.inputs[0].links))
                
    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        
        print("Copying from node ", node)
 
    # Free function to clean up on removal.
    def free(self):
        
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):

        layout.prop(bpy.data.materials[self.materialIndex], "name", text="", icon="MATERIAL_DATA")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
#    def draw_buttons_ext(self, context, layout):
#        layout.prop(self, "myFloatProperty")
#        # myStringProperty button will only be visible in the sidebar
#        layout.prop(self, "myStringProperty")

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Material Node"




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
    bpy.utils.register_class(MaterialNode)        
    bpy.utils.register_class(GraphScene)

    bpy.types.NODE_HT_header.append(SceneNodesHeader)

    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)
    


def unregister():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")

    bpy.utils.unregister_class(MyCustomTree)
    bpy.utils.unregister_class(MyCustomSocket)
    bpy.utils.unregister_class(SceneNode)
    bpy.utils.unregister_class(MaterialNode)            
    bpy.utils.register_class(ObjectNode)
    bpy.utils.unregister_class(GraphScene)

#if __name__ == "__main__":
#    register()
#    

register()    
