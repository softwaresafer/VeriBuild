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

% OK, so a lot of what you see here is plain silliness, but it sure made
% writing everything a lot more enjoyable. So think kindly on me! :-)

%%%%%%%%%%%%%%%%%
% Prolog format %
%%%%%%%%%%%%%%%%%
%
% NODES
%
% main_target(all).
% makefile(m0, ['', 'case', 'ica', 'project', 'deelproject', 'sekr', 'serverjobs', 'celkern'], 'Makefile', 21).
% target(t32_dep, dep).
% in_makefile(t32_dep, m0).
% target_concern(t32_dep, 0).%ismeta
% phony_target(t43_phony).
% build_time(t32_dep, 98).
% build_error(t32_dep).
% path_to_target(t489, ['', 'kava', 'ica', 'project', 'algemeen', 'forms']).
%
%
% EDGES
%
% dependency(t32_dep, t43_phony, t32_dep:t43_phony).
% dependency_type(t32_dep:t43_phony, 1).%ismeta
% dependency_time(t32_dep:t43_phony, 789).
% dependency_pruned(t32_dep:t43_phony, 0).
% dependency_implicit(t32_dep:t43_phony, 0).

:- write('Jeff Tracy: OK, boys. That\'s the brief. It\'s our first assignment, so make it look good.\n'),
   %consult(linux-facts),
   consult(case-facts),

   write('Jeff Tracy: 3...\n'),
   consult(make-logic),

   write('Jeff Tracy: 2...\n'),
   consult(gdf-dump),

   write('Jeff Tracy: 1...\n'),
   %consult(gdf-linux),
   consult(gdf-case),

   write('Jeff Tracy: Thunderbirds are go!\n'),

   %true.
   dump, write('Voice-off: Another successful mission by International Rescue.\n'), halt.
