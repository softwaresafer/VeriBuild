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
% Level: gdf generation.

dump_and_halt :-
	write('***START***'),nl,
 dump,
	write('***END***'),nl,
 halt
 .

dump :-
  % Allow the user to prepare some data in advance.
  once(gdf_prepare),

  % Open the outsputstream...
  open('out.gdf', write, Out),

  % Node definitions...
  gdf_nodedef_header(NodeDef),
  fputs(Out, ['nodedef> ', NodeDef, '\n']),
  forall(gdf_target(Key, Name),
      (gdf_node(Key, Name, Node),
       fputs(Out, Node))),

  write('***TARGETS FINISHED***'),nl,

  % Edge definitions...
  gdf_edgedef_header(EdgeDef),
  fputs(Out, ['edgedef> ', EdgeDef, '\n']),
  forall(gdf_dependency(Target, Dependency, Key),
      (gdf_edge(Target, Dependency, Key, Edge),
       fputs(Out, Edge))),

  write('***EDGES FINISHED***'),nl,

  % Close the outputstream...
  close(Out).


% =============================================================================
% fputs/2 :
%   Takes a stream and a list, and feeds each element in turn to write/2, again
%   passing on the stream argument.
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

fputs(_, []).

fputs(Out, [Head|Rest]) :- 
  write(Out, Head), 
  fputs(Out, Rest).

% >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>





