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

:-dynamic include_dependency_a/2.
:-dynamic include_target_a/2.
:-dynamic folder_target_a/2.
:-multifile custom_target/1.
:-multifile custom_dependency/3.

% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: basic make abstractions.

base_cached :-
%  forall(include_dependency(A, B, C),
%      assert(include_dependency_a(A, B, C))),
%  forall(included_target(Included, IncludedName),
%      assert(included_target_a(Included, IncludedName))),
	forall(folder_target(Folder, FolderName),
	assert(folder_target_a(Folder, FolderName))),
	forall(dependency(Src,Dst,Key),
	assert(rdependency(Dst,Src,Key))).


% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: bonus.
% Uses: basic make abstractions.  ((((((((((((((((((((((((((((((((( CACHED ))))
% 

header_target(Target) :-
  target_concern(Target, 'h').

autoconf_target(Target) :-
  target(Target,'autoconf.h').
  
%header_dep_edge(Key) :-
%  header_target(Dependency),
%  rdependency(Dependency,_, Key).

is_base_dependency(Key):-
  dependency_type(Key,0).

is_base_target(Target):-
  once(((rdependency(Target,_,Key);dependency(Target,_,Key)),is_base_dependency(Key))).

is_gcc_dep_target(Target):-
  (target_concern(Target, 'd');target_concern(Target, 'tmp');target_concern(Target, 'cmd');target_concern(Target, 'ver');(target_concern(Target,'o'),rdependency(Target,OTarget,_),target_concern(OTarget,'o'),target(Target,TName),concat_atom(['',OName],'.tmp_',TName),target(OTarget,OName))),
  \+ dependency(Target,_,_).

is_gcc_dep_dependency(_,Dependency):-
	is_gcc_dep_target(Dependency)
    .


% =============================================================================
% These predicates relate to the use of "includes" in makefiles (meta-edges).
% -----------------------------------------------------------------------------
% include_dependency/3:
%   Predicate allowing for the identification of dependencies which are really
%   "includes" in makefiles (flagged by makao with a "concern" of value 1).
%
% included_target/2:
%   Identifies targets which are pointed to by include dependencies, and only
%   by include dependencies. If it is pointed to by a dependency other than an
%   include one then that dependency takes "precedence" and the target loses
%   its included status.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

include_dependency(Target, Dependency, Key) :-
  dependency(Target, Dependency, Key),
  dependency_type(Key, 1).

included_target(Included, Name) :-
  target(Included, Name),
%  once(include_dependency(TargetA, Included, KeyA)),  % <--------------------- Note (A)
  once(include_dependency(_, Included, _)),  % <--------------------- Note (A)
%        include_dependency(TargetA, Included, KeyA))),
  forall(rdependency(Included, TargetB, KeyB),
      include_dependency(TargetB, Included, KeyB)).

% (A) The "once" is here for two reasons. One is that an included target must
%     be pointed to in an include dependency at least once (the following
%     forall does not do this). The other is to ensure that each target gets
%     flagged at most once as an included target. That is, if there are two (or
%     more) inclusions of a target, it really only needs to be said once that
%     it has been included.

% =============================================================================
% These predicates relate to the use of "force" in makefiles.
% -----------------------------------------------------------------------------
% force_target/2:
%   Predicate allowing for the identification of force targets.
%
% force_dependency/3:
%   Predicate allowing for the identification of dependencies which play part
%   in "force" rules.
%
% forced_target/2:
%   Uses the above predicates to allow for the identification of targets which
%   have been "forced".
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

makebuild_target(MakeBuild, 'Makefile.build') :-
  target(MakeBuild, 'Makefile.build').

% - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

makebuild_dependency(Target, MakeBuild, Key) :-
  makebuild_target(MakeBuild, _),
  rdependency(MakeBuild, Target, Key).

% - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

force_target(Force, 'FORCE') :-
  target(Force, 'FORCE').

% - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

force_dependency(Target, Force, Key) :-
  force_target(Force, _),
  rdependency(Force, Target, Key).

% - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

forced_target(Target, Name) :-
  force_target(Force, 'FORCE'),
  force_dependency(Target, Force, _),
  target(Target, Name).
  
% =============================================================================
% looping_dependency/3:
%   A dependency is considered looping when its Source and Target are the same.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

looping_dependency(X, X, Key) :-
  dependency(X, X, Key).

% =============================================================================
% folder_target/2:  +++++++++++++++++++++++++++++++++++++++++ EXPERIMENTAL ++++
%   This predicate may be used for identifying which targets are folders in a
%   filesystem.
%
% We recognize folders using the following strategy/logic:
% 1. Every physical target which has to be built will have an associated path.
%    These are tracked with path_to_target/2.
% 2. The last element in each path is a folder name (this is how Makao sets it
%    up).
% 3. Every node whose name (i.e. Name in target(T, Name)) matches a foldername
%    is likely to be a folder.
% In this reasoning it is step (3) which is, of course, the most tentative.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

folder_target(Folder, Name) :-
  %phony_target(Folder),  % <----------------------------------------- Note (B)
  target(Folder, Name),%BRAM: look for unknown concerns? assert all P's names once? OK (see base_cached)
  once((path_to_target(_, P),
        last(P, Name))).

% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% (B) This is an extra requirement, based on observation of results in the
%     linux build. Without this, another two targets would be selected as a
%     folder: t20 (include/asm) and t363 (scripts/genksyms). I'm not sure yet
%     whether these are real folders.
%
%     UPDATE: Bram has confirmed these as folders. I have therefore removed
%     this restriction. This seems to have a negative impact on performance
%     though (phony_target/1 cut down considerably on the search space), so I
%     added caching of this.

% =============================================================================
% unix_path/2:
%   For each target, what is its full path (including the target itself) ? The
%   path is returned in a unix format (one atom; using '/' as the folder
%   separator; with relative references resolved).
%
% simplify_path/3:
%   This is just the workhorse used by unix_path/2 for resolving the relative
%   references.
%   CAVEAT: This was written quick and dirty, and could do with a good
%           brushing.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

unix_path(Target, UnixPathToTarget) :-
  target(Target, Name),
  path_to_target(Target, Path),
  append(Path, [Name], PathToTarget),
  simplify_path([], PathToTarget, SimplifiedPathToTarget),
  concat_atom(SimplifiedPathToTarget, '/', UnixPathToTarget).

% - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

simplify_path(Path, [], Path).

simplify_path(Path, [End], Simplified) :-
  \+ End == '.',
  \+ End == '..',
  append(Path, [End], Simplified).

simplify_path(Prev, ['.' | Rest], Simplified) :-
  simplify_path(Prev, Rest, Simplified).

simplify_path(Prev, [Up | ['..' | Rest]], Simplified) :-
  \+ Up == '.',
  append(Prev, Rest, Todo),
  simplify_path([], Todo, Simplified).

simplify_path(Prev, [Up | [Here | Rest]], Simplified) :-
  \+ Up == '.',
  \+ Here == '..',
  append(Prev, [Up], Current),
  simplify_path(Current, [Here | Rest], Simplified).

% >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>






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

ms_target(Target, Name) :-
%  target(Target, Name),
%  \+ force_target(Target, Name),
%  \+ included_target_a(Target, Name).  % <- ((((((((((((((((( USE OF CACHE ))))
	target(Target, Name),
	is_base_target(Target),
				%  \+ header_target(Target),
	\+ is_gcc_dep_target(Target),
	\+ force_target(Target,_),
%	\+ makebuild_target(Target,_),
	\+ custom_target(Target).

ms_dependency(Target, Dependency, Key) :-
%  dependency(Target, Dependency, Key),
%  \+ looping_dependency(Target, Dependency, Key),
%  \+ include_dependency_a(Target, Dependency, Key),  % <- ((( USE OF CACHE ))))
%  \+ included_target_a(Target, _),  % <- (((((((((((((((((((( USE OF CACHE ))))
%  %\+ included_target_a(Dependency, _),  % <-------------------------- Note (A)
%  \+ force_dependency(Target, Dependency, Key).
	dependency(Target, Dependency, Key),
	is_base_dependency(Key),
				%  \+ header_dep_edge(Key),
	\+ looping_dependency(Target, Dependency, Key),
	\+ is_gcc_dep_dependency(Target,Dependency),
	\+ force_dependency(Target,Dependency,Key),
%	\+ makebuild_dependency(Target,Dependency,Key),
        \+ custom_dependency(Target,Dependency,Key).

%ms_cached :-
%  forall(spurious_dependency(A, B, C),
%    assert(spurious_dependency_a(A, B, C))).

% (A) This is not needed as it is part of include_dependency/3.

% =============================================================================
% These predicates define the concept of spurious dependencies.
% -----------------------------------------------------------------------------
% spurious_dependency/3:
%   A dependency Spurious is a dependency between two targets Src and Tgt for
%   which there exists a longer dependency_path.
%
% ms_interdependent/2:
%   Two targets Src and Tgt are dependent when there exists a path through the
%   dependencies from Src to Tgt.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

%spurious_dependency(Src, Tgt, Spurious) :-
%  \+ Src == Tgt,
%  ms_dependency(Src, Intermediate, _),
%  % \+ Src == Intermediate,  % <-------------------------------------- Note (B)
%  ms_interdependent(Intermediate, Tgt),
%  ms_dependency(Src, Tgt, Spurious).

% - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

%ms_interdependent(Src, Tgt) :-
%  ms_dependency(Src, Tgt, _).

%ms_interdependent(Src, Tgt) :-
%  \+ ms_dependency(Src, Tgt, _),
%  ms_dependency(Src, Intermediate, _),
%  % \+ Src == Intermediate,  % <-------------------------------------- Note (B)
%  ms_interdependent(Intermediate, Tgt).

% (B) This condition is already part of ms_dependency. I leave it here for
%     illustrative purposes (and so I won't forget).
% >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>



% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: abstraction (abs).
% Uses: make simplification (ms).  (((((((((((((((((((((((((((((((( CACHED ))))
% 

abs_cached:-
	forall(ms_target(Target, Name),
	       assert(ms_target_a(Target, Name))),
	forall(ms_dependency(Target, Dep,Key),
	       assert(ms_dependency_a(Target, Dep,Key))).

is_leaf_c_target(Target):-
	target_concern(Target,'c'),
	\+ms_dependency_a(Target,_,_).

abs_target(Target,Name):-
	ms_target_a(Target,Name),
	\+is_leaf_c_target(Target).

abs_dependency(Target,Dep,Key):-
	ms_dependency_a(Target,Dep,Key),
	\+is_leaf_c_target(Dep).

% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: composite (com), i.e. the one on which circular dependency chain can be seen.
% Uses: abstraction (abs).  (((((((((((((((((((((((((((((((( CACHED ))))
% 

com_cached:-
	forall(abs_target(Target, Name),
	       assert(abs_target_a(Target, Name))),
	forall(abs_dependency(Target, Dep,Key),
	       assert(abs_dependency_a(Target, Dep,Key))).

composite_target(Target):-
	abs_target_a(Target,_),
	target_concern(Target,'o'),
	forall(abs_dependency_a(Target,Dep,_),is_simple_o_target(Dep)).

is_simple_o_target(Target):-
	target_concern(Target,'o'),
	\+ abs_dependency_a(Target,_,_).

com_target(Target,Name):-
	abs_target_a(Target,Name),
	\+ is_simple_o_target(Target)
	.

com_dependency(Target,Dep,Key):-
	abs_dependency_a(Target,Dep,Key),
	\+ is_simple_o_target(Dep).


% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: component construction (cc).
% Uses: make simplification (ms).  (((((((((((((((((((((((((((((((( CACHED ))))
% 
% 1. We see all ms_targets except folders.
% 2. We see all ms_dependencies except for spurious ones, and those to and/or
%    from folders. <--> BRAM: you lose valuable dependencies this way!

cc_target(Target, Name) :-
  ms_target(Target, Name),
  \+ folder_target_a(Target, Name).  % <- ((((((((((((((((((( USE OF CACHE ))))

cc_dependency(Target, Dependency, Key) :-
  ms_dependency(Target, Dependency, Key),
  \+ folder_target_a(Target,_),  % <- ((((((((((((((((((((((( USE OF CACHE ))))
  \+ folder_target_a(Dependency,_).%,  % <- ((((((((((((((((((( USE OF CACHE ))))
%  \+ spurious_dependency_a(Target, Dependency, Key).  % <- (( USE OF CACHE ))))

% =============================================================================
% constructive_dependency/3:
%   A dependency Dep between two targets Target and Source is considered a
%   constructive dependency when the concern associated with Target may be built
%   from the concern associated with Source.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

constructive_dependency(Target, Source, Dep) :-
  cc_dependency(Target, Source, Dep),
  target_concern(Target, TargetConcern),
  target_concern(Source, SourceConcern),
  concern_built_from_concern(TargetConcern, SourceConcern).

% - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

% These are defined by the user, but should be reusable in most cases (which is
% why I keep track of them here).
concern_built_from_concern('h', 'h_shipped').
concern_built_from_concern('c', 'c_shipped').
concern_built_from_concern('c', 'uni').
concern_built_from_concern('o', 'h').
concern_built_from_concern('o', 'c').
concern_built_from_concern('o', 'ec').
concern_built_from_concern('o', 'S').
concern_built_from_concern('o', 's').
concern_built_from_concern('o', 'o').
concern_built_from_concern('so', 'o').
concern_built_from_concern('o', 'so').
concern_built_from_concern('so', 'lds').
concern_built_from_concern('a', 'o').
concern_built_from_concern('class', 'java').

% =============================================================================
% component_part_target/2:
%   This predicate identifies targets which may be used to build something
%   else (in the concern_built_from_concern/2 sense), but which are not themselves
%   built in this way from other parts.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

component_part_target(Target, Name) :-
  % It is a target...
  cc_target(Target, Name),
  % Which has no (constructive) dependencies...
  \+ cc_dependency(Target, _, _),
  % But which may be used to build something else...
  once((target_concern(Target, Concern),
        concern_built_from_concern(_, Concern))).

% =============================================================================
% component_target/2:
%   A component is something which gets built (in the concern_built_from_concern/2
%   sense) from other parts or components. In addition it may have no other
%   concern of dependency.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

component_target(Target, Name) :-
  % It is a target...
  cc_target(Target, Name),
  % Which has at least one constructive dependency...
  once(constructive_dependency(Target, _, _)),
  % And all its dependencies are constructive dependencies to other parts or
  % components...
  forall(cc_dependency(Target, Dependency, Key),
      (constructive_dependency(Target, Dependency, Key),
       (component_part_target(Dependency, _)
       ;component_target(Dependency, _)))).

% =============================================================================
% used_component_target/2:
%   A component is considered "used" when it is named as a dependency by
%   something which does not use it to build something else (again, in the
%   concern_built_from_concern/2 sense).
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

used_component_target(Target, Name) :-
  % It is a component...
  component_target(Target, Name),
  % Which is referred to in at least one non-constructive way...
  once((cc_dependency(Referrer, Target, Key),
       \+ constructive_dependency(Referrer, Target, Key))).

% >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: more alternative linux make idiom (alt2_lmi).
% Uses: composite level.  ((((((((((((((((((((((((((((((((( CACHED ))))
% 

alt2_lmi_cached:-
	forall(ms_target(Target, Name),
	       assert(ms_target_a(Target, Name))),
	forall(ms_dependency(Target, Dependency, Key),
	       assert(ms_dependency_a(Target, Dependency, Key))).

alt2_lmi_target(Target, Name) :-
  ms_target_a(Target, Name),
  \+folder_target_a(Target, Name).

alt2_lmi_dependency(Target, Dependency, Key) :-
  ms_dependency_a(Target, Dependency, Key),
  \+(folder_target_a(Target,_);folder_target_a(Dependency,_)).

% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: alternative linux make idiom (alt_lmi).
% Uses: composite level.  ((((((((((((((((((((((((((((((((( CACHED ))))
% 

alt_lmi_cached:-
	forall(ms_target(Target, Name),
	       assert(ms_target_a(Target, Name))),
	forall(ms_dependency(Target, Dependency, Key),
	       assert(ms_dependency_a(Target, Dependency, Key))).	

alt_lmi_target(Target, Name) :-
  ms_target_a(Target, Name).

alt_lmi_dependency(Target, Dependency, Key) :-
  ms_dependency_a(Target, Dependency, Key),
  \+((alt_recursive_make_idiom(Build,Folder,_),((Build == Target,Folder == Dependency);(Build == Dependency,Folder == Target)))).

% =============================================================================
% alt_linux___build_target/2:
%   This identifies the "__build" target which is central to the recursive
%   pattern in linux's makefiles.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

alt_linux___build_target(Build, '__build') :-
  ms_target_a(Build, '__build').

% =============================================================================
% alt_recursive_make_idiom/3:
%   This describes the recursive pattern itself. The predicate is satisfied
%   once per participating folder (as in folder_target/2).
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

alt_recursive_make_idiom(Build, Folder, Name) :-
  folder_target_a(Folder, Name), % <- ((((((((((((((((((((((( USE OF CACHE ))))
  alt_linux___build_target(Build, _),
  ms_dependency_a(Build, Folder, _), % <------------------------------- Note (A)
  ms_dependency_a(Folder, Build, _),
  once((ms_dependency_a(SimpleObject, Folder, _),
        target_concern(SimpleObject, 'o'),
		ms_dependency_a(CompositeObject, SimpleObject, _),
		target_concern(CompositeObject, 'o'))),
  ms_dependency_a(Build, CompositeObject, _).


% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: linux make idiom (lmi).
% Uses: composite level.  ((((((((((((((((((((((((((((((((( CACHED ))))
% 

:-dynamic composite_target_a/1.

lmi_cached:-
	forall(com_target(Target, Name),
	       assert(com_target_a(Target, Name))),
	forall(com_dependency(Target, Dep,Key),
	       assert(com_dependency_a(Target, Dep,Key))),
	forall(composite_target(Target),
	       assert(composite_target_a(Target))).	

lmi_target(Target, Name) :-
  com_target_a(Target, Name).

lmi_dependency(Target, Dependency, Key) :-
  com_dependency_a(Target, Dependency, Key),
  \+((recursive_make_idiom(Build,Folder,_),((Build == Target,Folder == Dependency);(Build == Dependency,Folder == Target)))).

% =============================================================================
% linux___build_target/2:
%   This identifies the "__build" target which is central to the recursive
%   pattern in linux's makefiles.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

linux___build_target(Build, '__build') :-
  com_target_a(Build, '__build').

% =============================================================================
% recursive_make_idiom/3:
%   This describes the recursive pattern itself. The predicate is satisfied
%   once per participating folder (as in folder_target/2).
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

recursive_make_idiom(Build, Folder, Name) :-
  folder_target_a(Folder, Name), % <- ((((((((((((((((((((((( USE OF CACHE ))))
  linux___build_target(Build, _),
  com_dependency_a(Build, Folder, _), % <------------------------------- Note (A)
  com_dependency_a(Folder, Build, _),
  once((com_dependency_a(SimpleObject, Folder, _),
        target_concern(SimpleObject, 'o'),
		com_dependency_a(CompositeObject, SimpleObject, _),
		target_concern(CompositeObject, 'o'))),
  com_dependency_a(Build, CompositeObject, _).

% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% (A) This dependency will satisfy spurious_dependency/3 in the ms level.

% =============================================================================
% preparation_idiom/2:
%   This describes the prepare idiom. The predicate is satisfied once
%   for every participating folder (as in folder_target/2).
%
% CAVEAT: I don't really understand this idiom yet, though I can clearly see
%         the pattern. Still, I should admit that I need to look deeper into
%         this.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

preparation_idiom(Folder, Name) :-
  lmi_target(Prepare, 'prepare'),
  lmi_target(Scripts, 'scripts'),
  lmi_dependency(Folder, Prepare, _),
  lmi_dependency(Folder, Scripts, _),
  folder_target_a(Folder, Name). % <- ((((((((((((((((((((((( USE OF CACHE ))))


% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: linux make idiom (postlmi).
% Uses: lmi level.  ((((((((((((((((((((((((((((((((( CACHED ))))
% 

post_cached:-
	forall(lmi_target(Target, Name),
	       assert(lmi_target_a(Target, Name))),
	forall(lmi_dependency(Target, Dep,Key),
	       assert(lmi_dependency_a(Target, Dep,Key))).	

is_leaf_folder(Target):-
	folder_target_a(Target,_),
	\+ lmi_dependency_a(Target,_,_).

post_target(Target, Name) :-
  lmi_target_a(Target, Name),
  \+ is_leaf_folder(Target).

post_dependency(Target, Dependency, Key) :-
  lmi_dependency_a(Target, Dependency, Key),
  \+ is_leaf_folder(Dependency).