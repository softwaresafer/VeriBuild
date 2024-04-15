/*-*- prolog -*-*/

% ***** BEGIN LICENSE BLOCK *****
% Version: MPL 1.1
%
% The contents of this file are subject to the Mozilla Public License Version
% 1.1 (the "License"); you may not use this file except in compliance with
% the License. You may obtain a copy of the License at
% http://www.mozilla.org/MPL/
%
% Software distributed under the License is distributed on an "AS IS" basis,
% WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
% for the specific language governing rights and limitations under the
% License.
%
% The Original Code is MAKAO.
%
% The Initial Developer of the Original Code is
% Bram Adams (bramATcsDOTqueensuDOTca).
% Portions created by the Initial Developer are Copyright (C) 2006-2010
% the Initial Developer. All Rights Reserved.
%
% Contributor(s):
%
% ***** END LICENSE BLOCK *****

%rule(name,target_list,edge_list):-call_to_predicate.

% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: basic make abstractions.

rule(include_dependency,[],[[Target,Dependency]]):-
    include_dependency(Target, Dependency, _)
    .

rule(included_target,[Included],[]):-
    included_target(Included, _)
    .

rule(force_target,[Force],[]):-
    force_target(Force, 'FORCE')
    .

rule(force_dependency,[],[[Target,Force]]):-
    force_dependency(Target, Force, _)
    .

rule(forced_target,[Target],[]):-
    forced_target(Target, _)
    .

rule(looping_dependency,[],[[X,X]]):-
    looping_dependency(X, X, _)
    .

rule(folder_target,[Folder],[]):-
    folder_target(Folder, _)
    .


% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: make simplification (ms).
% Uses: basic make abstractions.  ((((((((((((((((((((((((((((((((( CACHED ))))
% 
% 1. We see all targets except force targets.
% 2. We see all dependencies except (a) force dependencies, (b) include
%    dependencies and (c) looping ones.
%
% (1) and (2) should leave us without dangling dependencies. 
% (1), (2a) and (2c) should not change interdependency relationships.
% (2b) might (/will) change interdependency relationships, but we don't care
% about these, as include dependencies do not take part in the resolution of
% which targets need to be rebuilt.

rule(ms_target,[Target],[]):-
	ms_target(Target, _)
    .

rule(ms_dependency,[],[[Target,Dependency]]):-
	ms_dependency(Target, Dependency, _)
    .

rule(spurious_dependency,[],[[Src,Tgt]]):-
	spurious_dependency(Src, Tgt, _)
    .

rule(ms_interdependent,[],[[Src,Tgt]]):-
	ms_interdependent(Src, Tgt)
    .

% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: component construction (cc).
% Uses: make simplification (ms).  (((((((((((((((((((((((((((((((( CACHED ))))
% 
% 1. We see all ms_targets except folders.
% 2. We see all ms_dependencies except for spurious ones, and those to and/or
%    from folders. <--> BRAM: you lose valuable dependencies this way!

rule(cc_target,[Target],[]):-
	cc_target(Target, _)
    .

rule(cc_dependency,[],[[Target,Dependency]]):-
	cc_dependency(Target, Dependency, _)
    .

rule(constructive_dependency,[],[[Target,Source]]):-
	constructive_dependency(Target, Source, _)
    .

rule(component_part_target,[Target],[]):-
	component_part_target(Target, _)
    .

rule(component_target,[Target],[]):-
	component_target(Target, _)
    .


rule(used_component_target,[Target],[]):-
	used_component_target(Target, _)
    .

% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: linux make idiom (lmi).
% Uses: basic make abstractions.  ((((((((((((((((((((((((((((((((( CACHED ))))
% 

rule(lmi_target,[Target],[]):-
	lmi_target(Target, _)
    .

rule(lmi_dependency,[],[[Target,Dependency]]):-
	lmi_dependency(Target, Dependency, _)
    .

rule(linux___build_target,[Build],[]):-
	linux___build_target(Build, '__build')
    .

rule(recursive_make_idiom,[Folder],[]):-
	recursive_make_idiom(_, Folder, _)
    .

rule(preparation_idiom,[Folder],[]):-
	preparation_idiom(Folder, _)
    .