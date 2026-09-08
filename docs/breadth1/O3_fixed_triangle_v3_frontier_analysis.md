# O3 fixed-K3 V3 frontier analysis

## Status

V3.1 was stopped cleanly after 1.5 h. The structural T-skeleton WLOG partition has 72 cases, of which 29 were LRAT+Cake certified and 43 remained open. Exact labelled-pattern weight:

- certified/easy: 7.579303%
- hard frontier: 92.420697%

The purpose of this note is to record what the frontier data says structurally and to define the next reduction target. No SAT-hard case is treated as feasible; "hard" means only that CaDiCaL did not finish within the V3 leaf budget.

## 1. Exact easy/hard classifier on the s=0 branch

Let s=S(12,13). For each attachment group, the ordered pair of two-element T-neighbour sets has one of seven local D8-orbit types. Type 2 is represented by

- N12={0,1}
- N13={2,3}

with respect to the fixed matching {01,23}. Thus the two T-neighbour sets are the two complementary matching edges.

The V3.1 frontier has a striking exact split:

**For s=0, every one of the 22 certified root cases contains local type 2, and every one of the 40 hard root cases contains no local type 2.**

So, on the s=0 branch, the observed root classification is exactly

    contains type 2  <=>  certified in 22--66 s at the structural root,
    no type 2        <=>  timed out at 300 s and entered the hard frontier.

This is an empirical complexity classifier, not yet a mathematical implication. It is nevertheless strong evidence that the no-type-2 sector is the genuine structural core.

The s=1 branch is much smaller: 7 of 10 structural cases were certified; the only hard cases are

- k66_s1_t225
- k68_s1_t256
- k70_s1_t566

with total labelled-pattern weight only 0.268792%.

The main frontier is therefore the 40 s=0/no-type-2 classes, carrying 92.151905% of the total labelled T-skeleton weight.

## 2. Weight concentration

The hard frontier is strongly concentrated. The largest case k37_s0_t145 alone carries 11.946296% of all labelled T-skeletons. The eight largest hard classes together carry about 58.18% of the total labelled weight; the first twelve carry about 70.68%.

The dominant attached-common values are a=3 and a=4. Their hard weights are respectively 39.820987% and 41.998697%, so together they account for about 81.82% of the entire labelled T-skeleton space.

## 3. Why generic V3 splitting stalled

After the structural T-skeleton was fixed, every dynamic split used only four raw labelled variables:

- S(10,14): 43 splits
- S(10,15): 86 splits
- S(10,16): 172 splits
- S(10,17): 81 splits

No hard structural case was completed by these descendants. This is not merely weak branching: the split variables lie inside a large residual permutation symmetry that V3 did not quotient.

For s=0, if a is the number of attached vertices adjacent to both T vertices, then among the 18 ordinary unattached vertices the four cells according to adjacency to (12,13) have sizes

    O11 = 6-a,
    O10 = a,
    O01 = a,
    O00 = 12-a.

Hence the stabilizer of the fixed T-skeleton contains at least

    S_(6-a) x S_a x S_a x S_(12-a)

on the ordinary vertices, before considering any additional residual attachment-group symmetry. In the dominant cases this is enormous:

- a=3: S3 x S3 x S3 x S9
- a=4: S2 x S4 x S4 x S8

Thus raw binary splits on S(10,14), S(10,15), ... repeatedly distinguish vertices that are still equivalent under the residual stabilizer. V4 should classify a second-layer neighbourhood up to this stabilizer rather than continue labelled edge splitting.

For s=1 the ordinary-cell sizes are

    O11 = 1-a,
    O10 = 4+a,
    O01 = 4+a,
    O00 = 9-a,

with a in {0,1}.

## 4. Additional exact structure of L from the attachment equations

For every attachment group G and every attached vertex v, equation (13) gives

    sum_{u in G} P_uv = 1.

Since P=S+2L off the diagonal, this implies:

1. an attached vertex has no L-edge to any attached vertex;
2. it has exactly one S-neighbour in each of the three attachment groups.

Because an attached vertex has L-degree 1, its unique L-neighbour is therefore an ordinary unattached vertex (T has L-degree 0).

For an ordinary unattached vertex v, equation (13) gives weighted degree 2 into each attachment group. Hence, in each group, exactly one of the following occurs:

- one L-edge and no S-edge;
- two S-edges and no L-edge.

Consequently the L-graph on the 30 non-T length-3 orbits has:

- 12 attached vertices of L-degree 1;
- 18 ordinary vertices of L-degree 2;
- no attached-attached L-edges;
- exactly 12 attached-ordinary L-edges and 12 ordinary-ordinary L-edges.

Its components are therefore six paths with attached endpoints, together with zero or more cycles wholly inside the ordinary vertices.

This is a promising second-layer representation because the attachment-to-ordinary L incidence can be encoded by group modes rather than raw edge labels.

## 5. Four-cell partition forced by the two T vertices

Let A=C11, B=C10, C=C01, D=C00 be the four cells of the 30 non-T vertices according to S-adjacency to T=12,13.

### s=0

The total cell sizes are independent of a:

    |A|=6, |B|=6, |C|=6, |D|=12.

For every non-T vertex v with x=S(12,v), y=S(13,v), the T-row quotient equations imply

    weighted P-degree from N12 to v = 6-3x,
    weighted P-degree from N13 to v = 6-3y.

Let W_XY be the total P-weight between cells X,Y, with W_XX counting each undirected edge once. Then all aggregate cell weights are determined by a and one even integer p=W_AB=W_AC:

    W_AA=W_BB=W_CC=(18-p)/2,
    W_AB=W_AC=p,
    W_BC=36-p,
    W_AD=54-a-p,
    W_BD=W_CD=18+a+p,
    W_DD=39-a-p/2,

where 0 <= p <= 18 and p is even.

Thus the coarse 30-vertex P-structure has only ten possible aggregate values of p for each a, before using the much stronger attachment-group and S/L constraints.

### s=1

The total cell sizes are again independent of a:

    |A|=1, |B|=10, |C|=10, |D|=9.

The corresponding T-row equations give weighted degree from N12 to a vertex of type (x,y) as 6-3x-y, and symmetrically from N13 as 6-3y-x.

Writing p=W_AB=W_AC, the cell A has size one, so W_AA=0. The aggregate equations therefore force

    p=2.

Hence the entire coarse P-edge-weight table is fixed by a alone on the s=1 branch. This may be useful for attacking the three residual s=1 hard cases directly.

## 6. Recommended V4 direction

Do not resume V3's raw labelled binary cubing. The next branch should exploit the residual stabilizer explicitly.

A natural V4 coordinate is the neighbourhood of one attached vertex (for example vertex 10) relative to the four ordinary T-cells. Under the residual product of symmetric groups, a raw subset is determined first by its counts in the four cells. The unique L-neighbour of that attached vertex also contributes only its cell, not its label. Quotient equations with T=12,13 and the three attachment groups should constrain these count vectors strongly.

The resulting second-layer cases can then be canonically augmented under the residual group. Only after this quotient should any remaining SAT cubing be attempted.

A second, complementary direction is to use the L-path/cycle structure as the primary combinatorial object: six attached-to-attached paths through ordinary vertices plus possible ordinary cycles, decorated by the three attachment-group modes.

## 7. Certification discipline

Any extra symmetry reduction used in V4 must be stated as a WLOG theorem with an explicit group action and coverage argument. LRAT+Cake then certifies each reduced CNF, while the project-owned symmetry argument lifts UNSAT back to the full structural case. Raw SAT hardness is never accepted as evidence of impossibility.
