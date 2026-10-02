import { kindOf, splitList } from './books'

describe('kindOf', () => {
  it('identifica mangá', () => {
    expect(kindOf(['Aventura', 'Mangá'])).toBe('Mangá')
  })

  it('identifica quadrinhos', () => {
    expect(kindOf(['Quadrinhos', 'Fantasia'])).toBe('Quadrinhos')
  })

  it('assume livro quando não há tipo especial', () => {
    expect(kindOf(['Romance'])).toBe('Livro')
    expect(kindOf([])).toBe('Livro')
  })
})

describe('splitList', () => {
  it('separa por vírgula e remove espaços', () => {
    expect(splitList(' Aventura ,Fantasia,  Ação ')).toEqual(['Aventura', 'Fantasia', 'Ação'])
  })

  it('descarta itens vazios', () => {
    expect(splitList('a,, ,b,')).toEqual(['a', 'b'])
    expect(splitList('')).toEqual([])
  })
})
