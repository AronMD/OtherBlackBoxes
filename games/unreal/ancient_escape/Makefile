# Makefile generated by MakefileGenerator.cs
# *DO NOT EDIT*

UNREALROOTPATH = /opt/unreal-engine
GAMEPROJECTFILE =/home/kampff/NoBlackBoxes/repos/OtherBlackBoxes/boxes/games/unreal/ancient_escape/ancient_escape.uproject

TARGETS = \
	ancient_escape-Linux-DebugGame  \
	ancient_escape-Linux-Shipping  \
	ancient_escape \
	ancient_escapeEditor-Linux-DebugGame  \
	ancient_escapeEditor-Linux-Shipping  \
	ancient_escapeEditor \
	UnrealEditor-Linux-DebugGame  \
	UnrealEditor-Linux-Shipping  \
	UnrealEditor \
	UnrealGame-Linux-DebugGame  \
	UnrealGame-Linux-Shipping  \
	UnrealGame\
	configure

BUILD = bash "$(UNREALROOTPATH)/Engine/Build/BatchFiles/Linux/Build.sh"
PROJECTBUILD = "$(UNREALROOTPATH)/Engine/Binaries/ThirdParty/DotNet/6.0.302/linux/dotnet" "$(UNREALROOTPATH)/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll"

all: StandardSet

RequiredTools: CrashReportClient-Linux-Shipping CrashReportClientEditor-Linux-Shipping ShaderCompileWorker UnrealLightmass EpicWebHelper-Linux-Shipping

StandardSet: RequiredTools UnrealFrontend ancient_escapeEditor UnrealInsights

DebugSet: RequiredTools UnrealFrontend-Linux-Debug ancient_escapeEditor-Linux-Debug


ancient_escape-Linux-DebugGame:
	 $(PROJECTBUILD) ancient_escape Linux DebugGame  -project="$(GAMEPROJECTFILE)" $(ARGS)

ancient_escape-Linux-Shipping:
	 $(PROJECTBUILD) ancient_escape Linux Shipping  -project="$(GAMEPROJECTFILE)" $(ARGS)

ancient_escape:
	 $(PROJECTBUILD) ancient_escape Linux Development  -project="$(GAMEPROJECTFILE)" $(ARGS)

ancient_escapeEditor-Linux-DebugGame:
	 $(PROJECTBUILD) ancient_escapeEditor Linux DebugGame  -project="$(GAMEPROJECTFILE)" $(ARGS)

ancient_escapeEditor-Linux-Shipping:
	 $(PROJECTBUILD) ancient_escapeEditor Linux Shipping  -project="$(GAMEPROJECTFILE)" $(ARGS)

ancient_escapeEditor:
	 $(PROJECTBUILD) ancient_escapeEditor Linux Development  -project="$(GAMEPROJECTFILE)" $(ARGS)

UnrealEditor-Linux-DebugGame:
	 $(BUILD) UnrealEditor Linux DebugGame  -project="$(GAMEPROJECTFILE)" $(ARGS)

UnrealEditor-Linux-Shipping:
	 $(BUILD) UnrealEditor Linux Shipping  -project="$(GAMEPROJECTFILE)" $(ARGS)

UnrealEditor:
	 $(BUILD) UnrealEditor Linux Development  -project="$(GAMEPROJECTFILE)" $(ARGS)

UnrealGame-Linux-DebugGame:
	 $(BUILD) UnrealGame Linux DebugGame  -project="$(GAMEPROJECTFILE)" $(ARGS)

UnrealGame-Linux-Shipping:
	 $(BUILD) UnrealGame Linux Shipping  -project="$(GAMEPROJECTFILE)" $(ARGS)

UnrealGame:
	 $(BUILD) UnrealGame Linux Development  -project="$(GAMEPROJECTFILE)" $(ARGS)

configure:
	xbuild /property:Configuration=Development /verbosity:quiet /nologo "$(UNREALROOTPATH)/Engine/Source/Programs/UnrealBuildTool/UnrealBuildTool.csproj"
	$(PROJECTBUILD) -projectfiles -project="\"$(GAMEPROJECTFILE)\"" -game -engine 

.PHONY: $(TARGETS)
