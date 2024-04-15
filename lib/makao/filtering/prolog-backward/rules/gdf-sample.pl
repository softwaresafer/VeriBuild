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

% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
% Level: gdf generation of linux builds (gdf_linux).
% Uses: basic make abstractions.  ((((((((((((((((((((((((((((((((( CACHED ))))
% Uses: make simplification (ms).  (((((((((((((((((((((((((((((((( CACHED ))))
% Uses: component construction (cc).
% Uses: linux make idiom (lmi).
%
% 1. We see all ms-level targets except for folders participating in linux's
%    recursive make idiom or prepare idiom.
% 2. We see all ms-level dependencies except those to or from folders
%    participating in linux's recursive make idiom. The lost interdependencies
%    stemming from these will not be recaptured, as they will all point to
%    "__build" anyway (which does not matter much to us).

gdf_prepare :-
  base_cached,  % <------------------------------- Needed for ms and lmi level.
  abs_cached, % <------------------------------- Needed for abs level.
 com_cached. % <------------------------------- Needed for com level.
%  lmi_cached, % <------------------------------- Needed for lmi level.
%  post_cached. % <------------------------------- Needed for post level.
%%  ms_cached.  % <----------------------------------------- Needed for cc level.

custom_target(Target):-
  (autoconf_target(Target);(rdependency(Target,Au,_),autoconf_target(Au))).

custom_dependency(Target,Dependency,_):-
  (autoconf_target(Target);autoconf_target(Dependency)).

gdf_target(Target, Name) :-
	com_target(Target,Name).
%  target(Target, Name),
%  is_base_target(Target),
%%  \+ header_target(Target),
%  \+ is_gcc_dep_target(Target),
%  \+ force_target(Target,_).

gdf_dependency(Target, Dependency, Key) :-
	com_dependency(Target,Dependency,Key).
%  dependency(Target, Dependency, Key),
%  is_base_dependency(Key),
%%  \+ header_dep_edge(Key),
%  \+ is_gcc_dep_dependency(Target,Dependency),
%  \+ force_dependency(Target,Dependency,Key).


% The following would be nicer if we could rid the user of the formatting
% stuff (commas, newline).
gdf_nodedef_header('name,label,concern VARCHAR(32),folder BOOLEAN,component BOOLEAN,makefile VARCHAR(32),line INT').

gdf_node(Key, Name, [Key, ',', UnixPath, ',', Type, ',', Folder, ',', Component, ',', PathStr, ',', Line, '\n']) :-
   unix_path(Key, UnixPath),
   (once(target_concern(Key, Type))
     *-> true ;
         Type = ''),
   (once(folder_target_a(Key, Name))  % <- (((((((((((((((((( USE OF CACHE ))))
     *-> Folder = 'true' ; 
         Folder = 'false'),
   (once(composite_target_a(Key))
     *-> Component = 'true' ;
         Component = 'false'),
   in_makefile(Key, Makefile),
   makefile(Makefile,Path,File,Line),
   append(Path,[File],PathList),
   concat_atom(PathList,'/',PathStr).


gdf_edgedef_header('node1,node2,directed,implicit BOOLEAN,tstamp INT').

gdf_edge(Target, Dependency, Key, [Target, ',', Dependency, ',true,', Implicit, ',', Time, '\n']):-
	(once(dependency_implicit(Key,1))
	*-> Implicit = 'true' ;
	    Implicit = 'false'),
	(once(dependency_time(Key, TTime))
    *-> Time = TTime ;
	Time = -1)
	.


